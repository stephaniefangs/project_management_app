from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.loginPage, name="loginPage"),
    path('logout/', views.logoutPage, name="logoutPage"),
    path('home/', views.homePage, name="homePage"),
    path('admin_home/', views.adminPage, name="adminPage"),
    path('anonymous/', views.anonymousPage, name="anonymousPage"),
    path('login-redirect/', views.login_redirect, name='login_redirect'),
    path('calendar/', views.calendarPage, name='calendar'),
    path('create_event/', views.create_event, name='create_event'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/upload_file', views.uploadFiles, name="upload_file"),
    path('event/<int:event_id>/post-message/', views.post_message, name='post_message'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.update_profile, name='edit_profile'),
    path('event/<int:event_id>/request_join_event/', views.request_join_event, name='request_join_event'),
    path('events/<int:event_id>/approve/<str:username>/', views.approve_join_request, name='approve_join_request'),
    path('events/<int:event_id>/reject/<str:username>/', views.reject_join_request, name='reject_join_request'),
    path('event/<int:event_id>/leave/', views.leave_event, name='leave_event'),
    path('event/<int:event_id>/file/<int:file_id>/remove/', views.remove_file, name='remove_file'),
    path('my-events/', views.my_events, name='my_events'),
    path('search-events/', views.search_events, name='search_events')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)