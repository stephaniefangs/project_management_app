"""
Sources:
- Working with Amazon S3 Objects: ttps://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/s3-service-objects.html
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User as AuthUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount

class UserAccount(models.Model):
    # Unsure about needing to define the user types because the profile feature is in common user 
    USER_TYPES = (
        ('common', 'Common User'),
        ('pma_admin', 'PMA Administrator'),
        ('django_admin', 'Django Administrator')
    )
    
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200) 
    username = models.CharField(max_length=400)
    google_account = models.EmailField(max_length=254, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='common')
    profile_picture = models.URLField(max_length=1000, blank=True)  # For Google profile picture
    bio = models.TextField(blank=True)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username}"

    @property
    def is_pma_admin(self):
        return self.user_type == 'pma_admin'

    @property
    def is_django_admin(self):
        return self.user_type == 'django_admin'
    
@receiver(post_save, sender=AuthUser)
def create_or_update_user_account(sender, instance, created, **kwargs):  
    if created:
        try:
            social_account = SocialAccount.objects.get(user=instance)
            
            # Create new UserAccount 
            UserAccount.objects.create(
                auth_user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                username=instance.username,
                google_account=instance.email,
                user_type='common'
            )
            
        except Exception as e:
            print(f"Error in signal: {str(e)}")  # Debug 
            
    else:
        try:
            user_account = UserAccount.objects.get(auth_user=instance)
            user_account.first_name = instance.first_name
            user_account.last_name = instance.last_name
            user_account.username = instance.username
            user_account.google_account = instance.email
            user_account.save()
        except UserAccount.DoesNotExist:
            print(f"UserAccount not found for existing user: {instance.username}") # Debug

"""
class UserAccount(models.Model):
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200)
    last_name = models.TextField(blank=True)
    username = models.CharField(max_length=400)

    def __str__(self):
        return f"{self.username}"
"""


class Event(models.Model):
    event_name = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    location = models.CharField(max_length=200)
    startTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField(default=timezone.now)
    url = models.TextField(max_length=200, blank=True, null=True)
    owner = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='owned_events')
    members = models.ManyToManyField(AuthUser, related_name='events', blank=True)
    pending_members = models.ManyToManyField(AuthUser, related_name='pending_events', blank=True)

    def __str__(self):
        return self.event_name

# @receiver(post_save, sender=Event)
# def add_owner_as_member(sender, instance, created, **kwargs):
#     if created:
#         instance.members.add(instance.owner.auth_user)


class FileMetadata(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='files')
    file_name = models.CharField(max_length=255)  # Original filename
    file_title = models.CharField(max_length=255)  # User-provided title
    description = models.TextField()  
    keywords = models.CharField(max_length=500)  
    upload_timestamp = models.DateTimeField(default=timezone.now)
    s3_url = models.URLField(max_length=2000)
    file_type = models.CharField(max_length=20) 

    def __str__(self):
        return f"{self.file_title} ({self.file_name})"


class Message(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message by {self.author.username} on {self.created_at}"


@receiver(post_save, sender=AuthUser)
def create_or_update_user_account(sender, instance, created, **kwargs):
    if created:
        UserAccount.objects.create(
            auth_user=instance,
            first_name=instance.first_name,
            last_name= instance.last_name,
            username = instance.username,

        )
    else:
        user_account = UserAccount.objects.get(auth_user=instance)
        user_account.first_name = instance.first_name
        user_account.last_name = instance.last_name
        user_account.username = instance.username
        user_account.save()