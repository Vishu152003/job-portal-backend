import requests
import json

data = {
    'username': 'testuser999',
    'email': 'test999@example.com',
    'password': 'TestPass123!',
    'password_confirm': 'TestPass123!',
    'first_name': 'Test',
    'last_name': 'User',
    'role': 'seeker'
}

response = requests.post('http://127.0.0.1:8000/api/auth/register/', json=data)
print('Status:', response.status_code)
print('Response:', response.text)
