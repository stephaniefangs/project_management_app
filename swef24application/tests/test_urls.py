from django.test import SimpleTestCase, Client
from django.urls import resolve, reverse

from swef24application.views import loginPage, logoutPage, homePage, adminPage, login_redirect, calendarPage, uploadFiles, create_event, event_detail, anonymousPage, delete_event, delete_file, post_message, profile_view, update_profile, request_join_event,approve_join_request,reject_join_request,leave_event,remove_file,my_events, search_events

class TestUrls(SimpleTestCase):
    def test_loginPage(self):
        url = reverse('loginPage')
        self.assertEqual(resolve(url).func, loginPage)

    def test_logoutPage(self):
        url = reverse('logoutPage')
        self.assertEqual(resolve(url).func, logoutPage)

    def test_homePage(self):
        url = reverse('homePage')
        self.assertEqual(resolve(url).func, homePage)

    def test_adminPage(self):
        url = reverse('adminPage')
        self.assertEqual(resolve(url).func, adminPage)

    def test_login_redirect(self):
        url = reverse('login_redirect')
        self.assertEqual(resolve(url).func, login_redirect)

    def test_calendar(self):
        url = reverse('calendar')
        self.assertEqual(resolve(url).func, calendarPage)

    def test_create_event(self):
        url = reverse('create_event')
        self.assertEqual(resolve(url).func, create_event)

    def test_event_detail(self):
        url = reverse('event_detail', args=[1])
        self.assertEqual(resolve(url).func, event_detail)

    def test_upload_file(self):
        url = reverse('upload_file', kwargs={'event_id':1})
        self.assertEqual(resolve(url).func, uploadFiles)

    def test_post_message(self):
        url = reverse('post_message', kwargs={'event_id': 1})
        self.assertEqual(resolve(url).func, post_message)

    def test_delete_event(self):
        url = reverse('delete_event', kwargs={'event_id': 1})
        self.assertEqual(resolve(url).func, delete_event)

    def test_delete_file(self):
        url = reverse('delete_file', kwargs={'file_id': 1})
        self.assertEqual(resolve(url).func, delete_file)

    def test_profile_view(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func, profile_view)

    def test_update_profile(self):
        url = reverse('edit_profile')
        self.assertEqual(resolve(url).func, update_profile)

    def test_request_join_event(self):
        url = reverse('request_join_event', kwargs={'event_id': 1})
        self.assertEqual(resolve(url).func, request_join_event)

    def test_approve_join_request(self):
        url = reverse('approve_join_request', kwargs={'event_id': 1, 'username': 'testuser'})
        self.assertEqual(resolve(url).func, approve_join_request)

    def test_reject_join_request(self):
        url = reverse('reject_join_request', kwargs={'event_id': 1, 'username': 'testuser'})
        self.assertEqual(resolve(url).func, reject_join_request)

    def test_leave_event(self):
        url = reverse('leave_event', kwargs={'event_id': 1})
        self.assertEqual(resolve(url).func, leave_event)

    def test_remove_file(self):
        url = reverse('remove_file', kwargs={'event_id': 1, 'file_id': 1})
        self.assertEqual(resolve(url).func, remove_file)

    def test_my_events(self):
        url = reverse('my_events')
        self.assertEqual(resolve(url).func, my_events)
    def test_search_events(self):
        url = reverse('search_events')
        self.assertEqual(resolve(url).func, search_events)
    def test_anonymous(self):
        url = reverse('anonymousPage')
        self.assertEqual(resolve(url).func, anonymousPage)


# verify that the correct view function is invoked when a specific URL pattern is accessed