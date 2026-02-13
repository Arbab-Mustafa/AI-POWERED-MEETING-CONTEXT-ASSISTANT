"""
Test script to verify backend API endpoints are working correctly.
Run after starting the backend server with: python -m uvicorn app.main:app --reload
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_registration():
    """Test user registration endpoint."""
    print("\n=== Testing User Registration ===")
    
    data = {
        "email": "testuser@example.com",
        "name": "Test User",
        "password": "SecurePass123",
        "timezone": "UTC"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return response.json()
        elif response.status_code == 400:
            print("ℹ️ User already exists (expected if running test multiple times)")
            return None
        else:
            print(f"❌ Registration failed!")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_login(email, password):
    """Test user login endpoint."""
    print("\n=== Testing User Login ===")
    
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login successful!")
            print(f"Access Token: {result['access_token'][:50]}...")
            print(f"User: {result['user']['email']}")
            return result['access_token']
        else:
            print(f"❌ Login failed!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_get_current_user(token):
    """Test get current user endpoint."""
    print("\n=== Testing Get Current User ===")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Get user successful!")
            print(f"User Data: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Get user failed!")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_create_meeting(token):
    """Test create meeting endpoint."""
    print("\n=== Testing Create Meeting ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": "Test Meeting",
        "description": "This is a test meeting to verify API functionality",
        "start_time": "2026-02-20T10:00:00Z",
        "end_time": "2026-02-20T11:00:00Z",
        "attendees": [
            {"email": "attendee1@example.com", "name": "John Doe"},
            {"email": "attendee2@example.com", "name": "Jane Smith"}
        ],
        "meeting_link": "https://meet.google.com/test-meeting",
        "meeting_platform": "google_meet"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/meetings", json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Meeting created successfully!")
            print(f"Meeting ID: {result['id']}")
            print(f"Title: {result['title']}")
            return result['id']
        else:
            print(f"❌ Meeting creation failed!")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_list_meetings(token):
    """Test list meetings endpoint."""
    print("\n=== Testing List Meetings ===")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/meetings", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {len(result.get('meetings', []))} meetings")
            
            for meeting in result.get('meetings', [])[:3]:
                print(f"  - {meeting['title']} ({meeting['start_time']})")
            
            return True
        else:
            print(f"❌ List meetings failed!")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def run_all_tests():
    """Run all API tests."""
    print("=" * 60)
    print("ContextMeet API Test Suite")
    print("=" * 60)
    
    # Test registration
    reg_result = test_registration()
    
    # Test login (use either the new user or existing user)
    if reg_result:
        token = reg_result.get('access_token')
        email = reg_result.get('user', {}).get('email')
    else:
        # Try to login with existing test user
        token = test_login("testuser@example.com", "SecurePass123")
        email = "testuser@example.com"
    
    if not token:
        print("\n❌ Cannot proceed without valid token. Please check backend logs.")
        return False
    
    # Test get current user
    test_get_current_user(token)
    
    # Test create meeting
    meeting_id = test_create_meeting(token)
    
    # Test list meetings
    test_list_meetings(token)
    
    print("\n" + "=" * 60)
    print("Test Suite Complete!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend server!")
        print("Please ensure the backend is running on http://localhost:8000")
        print("\nStart it with:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")
