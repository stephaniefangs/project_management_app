from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import reverse
from .models import UserAccount

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        
        # Create UserAccount if it doesn't exist
        UserAccount.objects.get_or_create(
            auth_user=user,
            defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'google_account': user.email,
                'user_type': 'common'  # Set default user type
            }
        )
        
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Returns the URL to redirect to after successfully connecting a social account.
        """
        return reverse('login_redirect')