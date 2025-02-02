import requests
import json  # Ensure JSON library is imported
from utils.config import BASE_URL, AUTH_HEADERS
from utils.helpers import read_credentials
import pytest

# API Endpoints
USER_LOGIN = f"{BASE_URL}/user/account/check-user-exists-by-phone"
OTP_VERIFICATION = f"{BASE_URL}/user/account/validate-phone-otp"
NEW_USER_SIGNUP = f"{BASE_URL}/user/account/student-signup"

#Test credentials file path
CREDENTIALS_FILE = "credentials/phonenumber_signup.csv" 

# Test Function
@pytest.mark.parametrize("credentials",read_credentials(CREDENTIALS_FILE))
def test_user_flow(credentials):
    # Step 1: Check if this user is new or existing
    area_code = credentials["areacode"]
    phone_number = credentials["phonenumber"]

    payload = {"areaCode":area_code,"phoneNumber":phone_number} 
    (f"ending new user signup request...")
    response = requests.post(USER_LOGIN, json=payload, headers=AUTH_HEADERS)  # Fixed issue here
    print(f"API end point:{USER_LOGIN}")
    print(f"Auth headers: {AUTH_HEADERS}")
    print(f"Signup response status: {response.status_code}")
    print(f"Signup response text: {response.text}")
    print(f"Response headers: {response.headers}")
    assert response.status_code == 200,  f"Signup failed with status code {response.status_code}"
    

    # Check if response is JSON
    if response.headers.get("Content-Type", "").startswith("application/json"):
      response_data = response.json()
      print(f"Response JSON: {response_data}")
    # Process the JSON response
    else:
        print("Unexpected response type:")
        print(response.text)  # Debugging purposes
        print(f"response headers: {response.headers}")
        assert False, f"API returned an unexpected response type: {response.headers.get('Content-Type', '')}"


    # Proceed with processing the JSON response
    user_details = response_data.get("body", {})
    is_new_user = user_details.get("isNewUser", True)


    if is_new_user:
        print("New user detected. Redirected to signup flow...")

        # Step 2: Verify OTP for new user
        payload2= {
            "phoneNumber": phone_number,
            "areaCode": area_code,
            "otpCode": "123456",  # Replace with dynamic OTP if applicable
            "authType": "signup",
        }
        print(f"OTP Authentication Started...")
        response = requests.post(OTP_VERIFICATION, json=payload2, headers=AUTH_HEADERS)
        print(f"OTP Auth headers: {AUTH_HEADERS}")
        print(f"OTP response status: {response.status_code}")
        print(f"OTP response text: {response.text}")
        assert response.status_code == 200, "OTP validation failed"
        assert response.json().get("message") == "Success", f"Expected 'Success' but got '{response.json().get('message')}'"

        # Step 3: Test new user signup
        payload3 = {
            "name": "ashok",
            "childName": "ram",
            "dateOfBirth": "1994-03-11",
            "loginType": "phoneNumber",
            "deviceType": "web",
            "timezone": "652d2ab14eeb65744d58b772",
            "isGlobal": False,
            "phoneNumber": phone_number,
            "areaCode": area_code,
        }
        print(f"New user signup flow started...")
        response = requests.post(NEW_USER_SIGNUP, json=payload3, headers=AUTH_HEADERS)
        print(f"New user Auth headers: {AUTH_HEADERS}")
        print(f"New user Signup response status: {response.status_code}")
        print(f"New User Signup response text: {response.text}")
        assert response.status_code == 200, "Signup failed"
        assert response.json().get("message") == "Success", f"Expected 'Success' but got '{response.json().get('message')}'"

        print("Signup completed for new user.")

    else:
        print("Existing user detected. Logging in...")

        # Step 2: Verify OTP for existing user
        payload4 = {
            "phoneNumber": phone_number,
            "areaCode": area_code,
            "otpCode": "123456",  # Replace with dynamic OTP if applicable
            "authType": "login",
        }
        print(f"If Existing user login started...")
        response = requests.post(OTP_VERIFICATION, json=payload4, headers=AUTH_HEADERS)
        print(f"Existing user Auth headers: {AUTH_HEADERS}")
        print(f"Existing user Signup response status: {response.status_code}")
        print(f"Existing user Signup response text: {response.text}")
        assert response.status_code == 200, f"Expected 'Success' but got '{response.json().get('message')}'"

        is_verified = response.json().get("body", {}).get("isVerified", False)
        assert is_verified, "User verification failed"
        print("Login successful for existing user.")
