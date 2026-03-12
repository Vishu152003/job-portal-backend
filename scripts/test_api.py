import urllib.request
import urllib.parse
import json

def test_register():
    data = {
        'username': 'testuser123',
        'email': 'test123@example.com',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'Recruiter'
    }
    
    url = 'http://127.0.0.1:8000/api/auth/register/'
    headers = {'Content-Type': 'application/json'}
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print('Status:', response.status)
            print('Response:', response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('Status:', e.code)
        print('Error:', e.read().decode('utf-8'))

def test_login():
    data = {
        'username': 'testuser123',
        'password': 'TestPass123!'
    }
    
    url = 'http://127.0.0.1:8000/api/auth/login/'
    headers = {'Content-Type': 'application/json'}
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print('Status:', response.status)
            print('Response:', response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('Status:', e.code)
        print('Error:', e.read().decode('utf-8'))

if __name__ == '__main__':
    print("=== Testing Register ===")
    test_register()
    print("\n=== Testing Login ===")
    test_login()
