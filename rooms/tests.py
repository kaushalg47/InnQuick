from django.test import TestCase
from django.urls import reverse
from .models import Room
import json

class RoomAPITests(TestCase):
    def test_add_room_success(self):
        # Endpoint URL
        url = reverse('add_room')  # Adjust this to the correct name in your urls.py

        # Valid payload
        data = {'number': '101'}
        
        # Send POST request to add_room API
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        # Assert room creation was successful
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'Room created successfully')
        self.assertTrue('room_id' in response.json())
        self.assertTrue('room_url' in response.json())

    def test_add_room_missing_number(self):
        url = reverse('add_room')
        
        # Missing room number
        data = {}

        # Send POST request
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        # Assert bad request due to missing room number
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Room number is required')

    def test_add_room_duplicate_number(self):
        url = reverse('add_room')
        
        # First, create a room
        Room.objects.create(number='101')

        # Attempt to create a room with the same number
        data = {'number': '101'}
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        # Assert conflict due to duplicate room number
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Room number already exists')
