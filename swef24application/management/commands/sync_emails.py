from django.core.management.base import BaseCommand
from django.contrib.auth.models import User as AuthUser
from allauth.socialaccount.models import SocialAccount
from swef24application.models import UserAccount

class Command(BaseCommand):
    help = 'Sync emails from social accounts to user accounts'

    def handle(self, *args, **kwargs):
        for user in AuthUser.objects.all():
            try:
                social_account = SocialAccount.objects.get(user=user)
                email = social_account.extra_data.get('email', user.email)
                
                user_account = UserAccount.objects.get(auth_user=user)
                user_account.google_account = email
                user_account.save()
                
                user.email = email
                user.save()
                
                self.stdout.write(self.style.SUCCESS(f'Updated email for user {user.username}'))
            except (SocialAccount.DoesNotExist, UserAccount.DoesNotExist):
                continue