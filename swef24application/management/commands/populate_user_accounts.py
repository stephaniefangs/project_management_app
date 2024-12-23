from django.core.management.base import BaseCommand
from django.contrib.auth.models import User as AuthUser
from swef24application.models import UserAccount

class Command(BaseCommand):
    help = 'Populate UserAccount model for existing AuthUser instances'

    def handle(self, *args, **kwargs):
        for user in AuthUser.objects.all():
            UserAccount.objects.get_or_create(
                auth_user=user,
                defaults={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                }
            )
        self.stdout.write(self.style.SUCCESS('UserAccount instances populated for existing users.'))