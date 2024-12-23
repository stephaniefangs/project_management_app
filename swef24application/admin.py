from django.contrib import admin
from .models import Event
from .models import UserAccount
# Register your models here.
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'location', 'startTime', 'endTime')
admin.site.register(Event, EventAdmin)

class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('auth_user','username', 'first_name', 'last_name', )
admin.site.register(UserAccount, UserAccountAdmin)
