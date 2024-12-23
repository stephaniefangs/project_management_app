from django import forms
from .models import Event
from . import models
class CreateEvent(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = ['event_name', 'description', 'location', 'startTime', 'endTime', 'url']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("startTime")
        end_time = cleaned_data.get("endTime")

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("The start time must be before the end time.")

        return cleaned_data


class EventQueryForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = ['event_name', 'description', 'location', 'startTime', 'endTime', 'url']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("startTime")
        end_time = cleaned_data.get("endTime")

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("The start time must be before the end time.")

        return cleaned_data