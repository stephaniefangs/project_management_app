"""
Sources:
- How to delete files from amazon s3 bucket?: https://stackoverflow.com/questions/3140779/how-to-delete-files-from-amazon-s3-bucket
"""

import json
from django.contrib.auth.models import User as AuthUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django.core.files.storage import FileSystemStorage
from .forms import CreateEvent, EventQueryForm
import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError, ClientError
from .models import Event, FileMetadata, Message, UserAccount
from django.utils import timezone
from django.db.models import Q

@login_required
def profile_view(request):
    user_account = get_object_or_404(UserAccount, auth_user=request.user)
    
    context = {
        'user_account': user_account,
        'events_created': user_account.owned_events.count(),
        'events_participating': request.user.events.count(),
        'email': user_account.google_account 
    }
    return render(request, 'commonUserTemplates/profile.html', context)

@login_required
def update_profile(request):
    user_account = get_object_or_404(UserAccount, auth_user=request.user)
    
    if request.method == 'POST':
        user_account.bio = request.POST.get('bio', '')
        user_account.save()
        
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()
        
        return redirect('profile')
        
    context = {'user_account': user_account}
    return render(request, 'commonUserTemplates/editProfile.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('login_redirect')
    return render(request, "commonUserTemplates/loginPage.html")

@login_required
def homePage(request):
    if request.user.groups.filter(name='PMA Administrators').exists():
        return redirect('adminPage')
    
    events = Event.objects.all().order_by('startTime')

    current_events = [event for event in events if event.endTime > timezone.now()]
    past_events = [event for event in events if event.endTime <= timezone.now()]
    
    return render(request, "commonUserTemplates/homePage.html", {'current_events': current_events,
                                                                 'past_events': past_events})

@login_required
def login_redirect(request):
    if request.user.groups.filter(name='PMA Administrators').exists():
        return redirect('adminPage')
    else:
        return redirect('homePage')

def logoutPage(request):
    logout(request)
    return redirect('loginPage')

def anonymousPage(request):
    events = Event.objects.all().order_by('startTime')

    current_events = [event for event in events if event.endTime > timezone.now()]
    past_events = [event for event in events if event.endTime <= timezone.now()]

    return render(request, "commonUserTemplates/anonymousPage.html", {'current_events': current_events,
                                                                 'past_events': past_events})

def calendarPage(request):
    events = Event.objects.all()

    eventData = [{"title": event.event_name,
             "start": event.startTime.isoformat(),
             "end": event.endTime.isoformat(),
             "description": event.description,
             "url": event.url or ""} for event in events]

    return render(request, 'commonUserTemplates/calendar.html', {"events": json.dumps(eventData)})

@login_required
def create_event(request):
    context = {}
    if request.method == "POST":
        form = CreateEvent(request.POST)
        if form.is_valid():

            user_account = UserAccount.objects.get(auth_user=request.user)
            # this sets up our user account and now all we have to do is set the user to an event

            event = form.save(commit=False)
            event.owner = user_account
            event.save()
            return redirect('homePage')
        else:
            context['form'] = form
    else:
        form = CreateEvent()

    context['form'] = form
    return render(request, "commonUserTemplates/createEvent.html", context)

@login_required
def adminPage(request):
    if not request.user.groups.filter(name='PMA Administrators').exists():
        return redirect('homePage')
    
    events = Event.objects.all().prefetch_related('files').order_by('-startTime')
    return render(request, "commonUserTemplates/adminPage.html", {'events': events})

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

@login_required
def uploadFiles(request, event_id):
    context = {}
    event = get_object_or_404(Event, id=event_id)
    bucket_name = f"myapp-event-bucket-{event_id}"

    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name)
    try:
        s3_client.delete_public_access_block(Bucket=bucket_name)
        print(f"Public access block disabled for {bucket_name}.")
    except ClientError as e:
        print(f"Error disabling public access block: {e}")
        context['error'] = f"Error disabling public access block: {str(e)}"
        return render(request, "commonUserTemplates/uploadFile.html", context)
    public_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    try:
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(public_policy))
        print(f"Public read access granted to {bucket_name}.")
    except ClientError as e:
        print(f"Error applying public policy: {e}")
        context['error'] = f"Error applying public policy: {str(e)}"
        return render(request, "commonUserTemplates/uploadFile.html", context)

    if request.method == 'POST':
        if 'document' not in request.FILES:
            context['error'] = "No file selected. Please choose a file to upload."
        else:
            uploaded_file = request.FILES['document']
            file_name = uploaded_file.name
            file_title = request.POST.get('file_title', '').strip().lower()
            file_extension = file_name.split('.')[-1].lower()

            if FileMetadata.objects.filter(event=event, file_title__iexact=file_title).exists():
                context[
                    'error'] = f"A file with the title '{file_title}' already exists for this event. Please choose a different title."
            else:
                # Check file type
                content_type = None
                file_type = 'other'
                if file_extension == 'pdf':
                    content_type = 'application/pdf'
                    file_type = 'pdf'
                elif file_extension in ['jpg', 'jpeg', 'png']:
                    content_type = f'image/{file_extension}'
                    file_type = 'image'
                elif file_extension == 'txt':
                    content_type = 'text/plain'
                    file_type = 'text'
            
                if file_extension not in ['txt', 'pdf', 'jpg', 'jpeg', 'png']:
                    context['error'] = "Invalid file type. Only .txt, .pdf, or image files are allowed."
                else:
                    try:
                        # Upload to S3
                        extra_args = {'ContentType': content_type} if content_type else {}
                        s3_client.upload_fileobj(
                            uploaded_file,
                            bucket_name,
                            file_name,
                            ExtraArgs=extra_args
                        )
                        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

                        # Save metadata
                        FileMetadata.objects.create(
                            event=event,
                            file_name=file_name,
                            file_title=request.POST.get('file_title', file_name),
                            description=request.POST.get('description', ''),
                            keywords=request.POST.get('keywords', ''),
                            s3_url=file_url,
                            file_type=file_type
                        )

                        context['url'] = file_url
                        context['file_type'] = file_type
                        
                        """
                        if file_type == 'text':
                            text_content = uploaded_file.read().decode('utf-8')
                            context['file_content'] = text_content
                        """

                    except Exception as e:
                     context['error'] = f"An error occurred: {str(e)}"

    # Get files with metadata
    try:
        files = FileMetadata.objects.filter(event=event).order_by('-upload_timestamp')
        context['uploaded_files'] = [
            {
                'name': f.file_name,
                'title': f.file_title,
                'description': f.description,
                'keywords': f.keywords,
                'url': f.s3_url,
                'type': f.file_type,
                'upload_time': f.upload_timestamp
            } for f in files
        ]
    except Exception as e:
        context['error'] = f"Could not retrieve files: {str(e)}"

    context['event_id'] = event_id
    return render(request, "commonUserTemplates/uploadFile.html", context)

@login_required
def post_message(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        content = request.POST.get('message_content')
        if content:
            Message.objects.create(
                event=event,
                author=request.user,
                content=content
            )

        return redirect('event_detail', event_id=event_id)
    return redirect('event_detail', event_id=event_id)


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.duration = event.endTime - event.startTime

    context = {'event': event, 'pending_members': event.pending_members.all(),
               'event_id': event_id}

    messages = Message.objects.filter(event=event).select_related('author').order_by('-created_at')
    context['messages'] = messages
    
    try:
        files = FileMetadata.objects.filter(event=event).order_by('-upload_timestamp')
        uploaded_files = []
        for file in files:
            uploaded_files.append({
                'id': file.id, # Added this line for delete files for common user
                'name': file.file_name,
                'title': file.file_title,
                'description': file.description,
                'keywords': file.keywords,
                'url': file.s3_url,
                'type': file.file_type,
                'upload_time': file.upload_timestamp
            })
        context['uploaded_files'] = uploaded_files
    except Exception as e:
        context['error'] = f"Could not retrieve files: {str(e)}"

    return render(request, "commonUserTemplates/eventDetail.html", context)

@login_required
def my_events(request):
    user_account = UserAccount.objects.get(auth_user=request.user)
    
    # Get events where user is a member OR owner
    member_events = Event.objects.filter(members=request.user)
    owned_events = Event.objects.filter(owner=user_account)

    user_events = (member_events | owned_events).distinct()

    current_events = [event for event in user_events if event.endTime > timezone.now()]
    past_events = [event for event in user_events if event.endTime <= timezone.now()]
    
    return render(request, 'commonUserTemplates/myEvents.html', {
        'current_events': current_events,
        'past_events': past_events
    })

@login_required
def delete_event(request, event_id):
    curr_event = get_object_or_404(Event, id=event_id)

    if not (request.user.groups.filter(name='PMA Administrators').exists() or curr_event.owner.auth_user == request.user):
        return redirect('homePage')
    
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        # Delete associated S3 files
        for file in event.files.all():
            try:
                # Delete from S3
                bucket_name = f"myapp-event-bucket-{event_id}"
                s3_client.delete_object(
                    Bucket=bucket_name,
                    Key=file.file_name
                )
            except Exception as e:
                print(f"Error deleting file from S3: {str(e)}")
        
        event.delete()
        
    return redirect('adminPage')

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(FileMetadata, id=file_id)
    event_id = file.event.id
    if not (request.user.groups.filter(name='PMA Administrators').exists()):
        return redirect('homePage')

    if request.method == 'POST':
        try:
            # Delete from S3
            bucket_name = f"myapp-event-bucket-{event_id}"
            s3_client.delete_object(
                Bucket=bucket_name,
                Key=file.file_name
            )
        except Exception as e:
            print(f"Error deleting file from S3: {str(e)}")


        # Delete the file metadata
        file.delete()
        messages.success(request, "File deleted successfully.")

    return redirect('adminPage')

@login_required
def request_join_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user not in event.members.all():
        event.pending_members.add(request.user)
    return redirect('event_detail', event_id=event_id)

@login_required
def leave_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user in event.members.all():
        event.members.remove(request.user)
        messages.success(request, f"You have left the event '{event.event_name}'.")
    else:
        messages.error(request, "You are not a member of this event.")
    return redirect('event_detail', event_id=event_id)


def approve_join_request(request, event_id, username):
    event = get_object_or_404(Event, id=event_id)
    user = get_object_or_404(AuthUser, username=username)
    event.pending_members.remove(user)
    event.members.add(user)
    messages.success(request, f"{user.username} has been approved to join the event.")

    return redirect('event_detail', event_id=event.id)


def reject_join_request(request, event_id, username):
    event = get_object_or_404(Event, id=event_id)
    user = get_object_or_404(AuthUser, username=username)
    event.pending_members.remove(user)
    messages.success(request, f"{user.username} has been rejected from joining the event.")
    return redirect('event_detail', event_id=event.id)

@login_required
def remove_file(request, event_id, file_id):
    event = get_object_or_404(Event, id=event_id)
    file = get_object_or_404(FileMetadata, id=file_id, event=event)

    if request.user == event.owner.auth_user or request.user in event.members.all():
        try:
            # Delete from S3
            bucket_name = f"myapp-event-bucket-{event_id}"
            s3_client.delete_object(
                Bucket=bucket_name,
                Key=file.file_name
            )
        except Exception as e:
            print(f"Error deleting file from S3: {str(e)}")

        file.delete()
        messages.success(request, "File removed successfully.")
    else:
        messages.error(request, "You do not have permission to remove this file.")

    return redirect('event_detail', event_id=event.id)


@login_required()
def search_events(request):
    events = Event.objects.all()
    if request.method == "GET":
       # we will check events to get pretty much
        form = EventQueryForm(request.GET)
        form.is_valid()

        event_name = form.cleaned_data.get("event_name")
        location = form.cleaned_data.get("location")
        startTime = form.cleaned_data.get("startTime")
        endTime = form.cleaned_data.get("endTime")
        url = form.cleaned_data.get("url")

        query = Q()
        if event_name:
                query &= Q(event_name__icontains=event_name)
        if location:
                query &= Q(location__icontains=location)
        if startTime:
                query &= Q(startTime__gte=startTime)
        if endTime:
                query &= Q(endTime__lte=endTime)
        if url:
                query &= Q(url__icontains=url)

        events = Event.objects.filter(query)

        return render(request, "commonUserTemplates/eventSearchPage.html", {"events": events})
