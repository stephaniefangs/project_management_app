from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from swef24application.models import Event, UserAccount, AuthUser,SocialAccount
import json
import os
from django.conf import settings

# client = Client()
#
# class TestViews(TestCase):
#     def test_anonymousPage(self):
#
#         response = client.get(reverse('anonymousPage'))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "commonUserTemplates/anonymousPage.html")
#         self.assertTemplateUsed(response, "commonUserTemplates/footer.html")
#
#     def test_calendar_view_anonymous(self):
#         response = self.client.get(reverse('calendar'))
#         self.assertEqual(response.status_code, 200)