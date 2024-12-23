from django.test import SimpleTestCase
from datetime import datetime
from swef24application.forms import CreateEvent, EventQueryForm

class TestForms(SimpleTestCase):
    def test_valide_createEvent(self):
        #test a valid event
        data = {
            'event_name': 'Test Event',
            'description': 'Test event description',
            'location': 'Test location',
            'startTime': datetime(2024, 12, 4, 10, 0),
            'endTime': datetime(2024, 12, 5, 12, 0),
            'url': 'https://example.com'
        }

        form = CreateEvent(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_event_creation_start_after_end(self):
        # Test where startTime is after endTime
        data = {
            'event_name': 'Test Event',
            'description': 'Test event description',
            'location': 'Test location',
            'startTime': datetime(2024, 12, 5, 12, 0),
            'endTime': datetime(2024, 12, 5, 10, 0),
            'url': 'https://example.com'
        }

        form = CreateEvent(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'], ['The start time must be before the end time.'])

    def test_invalid_event_creation_start_equal_end(self):
        # Test where startTime is after endTime
        data = {
            'event_name': 'Test Event',
            'description': 'Test event description',
            'location': 'Test location',
            'startTime': datetime(2024, 12, 5, 10, 0),
            'endTime': datetime(2024, 12, 5, 10, 0),
            'url': 'https://example.com'
        }

        form = CreateEvent(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'], ['The start time must be before the end time.'])
    def test_valid_event_creation_q(self):
        # Valid case
        data = {
            'event_name': 'Test Event',
            'description': 'Test event description',
            'location': 'Test location',
            'startTime': datetime(2024, 12, 4, 10, 0),
            'endTime': datetime(2024, 12, 5, 12, 0),
            'url': 'https://example.com'
        }

        form = EventQueryForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_event_creation_start_after_end_q(self):
        # Invalid case where startTime is after endTime
        data = {
            'event_name': 'Test Event',
            'description': 'Test event description',
            'location': 'Test location',
            'startTime': datetime(2024, 12, 5, 12, 0),
            'endTime': datetime(2024, 12, 5, 10, 0),
            'url': 'https://example.com'
        }

        form = EventQueryForm(data=data)
        self.assertFalse(form.is_valid())  # Form should be invalid
        self.assertIn('__all__', form.errors)  # Check if the general error is raised
        self.assertEqual(form.errors['__all__'], ['The start time must be before the end time.'])