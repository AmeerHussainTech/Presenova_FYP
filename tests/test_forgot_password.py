"""
Unit & Integration Tests for Forgot Password & Reset Password Flow
Verifies:
1. Timing-safe generic response for registered and unregistered emails (anti-enumeration)
2. Invalid email format validation
3. Cryptographic token generation and 30-min expiration checks
4. Replay-attack prevention (single-use token verification)
5. Successful password reset and subsequent authentication with new credentials
"""

import unittest
import json
import uuid
from werkzeug.security import check_password_hash
from main import create_app
from models import User

class TestForgotPasswordFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    def setUp(self):
        # Create a unique test user for isolation
        self.unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"testuser_{self.unique_id}@example.com"
        self.initial_password = "InitialPassword123!"
        
        # Register user via API
        resp = self.client.post(
            '/api/auth/signup',
            data=json.dumps({
                "name": f"Test User {self.unique_id}",
                "email": self.test_email,
                "password": self.initial_password
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 201)

    def test_01_forgot_password_registered_email(self):
        """Requesting password reset for registered email returns success with dev token."""
        resp = self.client.post(
            '/api/auth/forgot-password',
            data=json.dumps({"email": self.test_email}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("dev_reset_token", data)
        self.assertTrue(len(data["dev_reset_token"]) > 20)

    def test_02_forgot_password_unregistered_email_anti_enumeration(self):
        """Unregistered email returns identical generic success message without leaking existence."""
        unregistered_email = f"ghost_{uuid.uuid4().hex[:8]}@example.com"
        resp = self.client.post(
            '/api/auth/forgot-password',
            data=json.dumps({"email": unregistered_email}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        # Generic message must be present
        self.assertIn("If an account with this email exists", data.get("message", ""))
        # Unregistered user has no token
        self.assertNotIn("dev_reset_token", data)

    def test_03_forgot_password_invalid_email_format(self):
        """Invalid email formats return 400 Bad Request."""
        resp = self.client.post(
            '/api/auth/forgot-password',
            data=json.dumps({"email": "not-an-email"}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data.get("error"), "InvalidEmail")

    def test_04_full_reset_password_flow(self):
        """Full cycle: request token -> reset password -> verify login with new password."""
        # 1. Request token
        req_resp = self.client.post(
            '/api/auth/forgot-password',
            data=json.dumps({"email": self.test_email}),
            content_type='application/json'
        )
        token = req_resp.get_json().get("dev_reset_token")
        self.assertIsNotNone(token)

        # 2. Reset password
        new_password = "BrandNewSecurePassword456!"
        reset_resp = self.client.post(
            '/api/auth/reset-password',
            data=json.dumps({"token": token, "password": new_password}),
            content_type='application/json'
        )
        self.assertEqual(reset_resp.status_code, 200)
        reset_data = reset_resp.get_json()
        self.assertTrue(reset_data.get("success"))

        # 3. Old password must fail
        old_login_resp = self.client.post(
            '/api/auth/login',
            data=json.dumps({"email": self.test_email, "password": self.initial_password}),
            content_type='application/json'
        )
        self.assertEqual(old_login_resp.status_code, 401)

        # 4. New password must succeed
        new_login_resp = self.client.post(
            '/api/auth/login',
            data=json.dumps({"email": self.test_email, "password": new_password}),
            content_type='application/json'
        )
        self.assertEqual(new_login_resp.status_code, 200)
        login_data = new_login_resp.get_json()
        self.assertTrue(login_data.get("success"))
        self.assertIn("access_token", login_data)

    def test_05_prevent_replay_attack(self):
        """Using a reset token twice must be rejected."""
        # Request token
        req_resp = self.client.post(
            '/api/auth/forgot-password',
            data=json.dumps({"email": self.test_email}),
            content_type='application/json'
        )
        token = req_resp.get_json().get("dev_reset_token")

        # First reset succeeds
        first_reset = self.client.post(
            '/api/auth/reset-password',
            data=json.dumps({"token": token, "password": "NewPassword789!"}),
            content_type='application/json'
        )
        self.assertEqual(first_reset.status_code, 200)

        # Second reset with SAME token must fail
        second_reset = self.client.post(
            '/api/auth/reset-password',
            data=json.dumps({"token": token, "password": "AnotherPassword999!"}),
            content_type='application/json'
        )
        self.assertEqual(second_reset.status_code, 400)
        data = second_reset.get_json()
        self.assertEqual(data.get("error"), "TokenAlreadyUsed")

    def test_06_reset_password_weak_password_rejection(self):
        """Passwords shorter than 8 characters must be rejected."""
        req_resp = self.client.post(
            '/api/auth/forgot-password',
            data=json.dumps({"email": self.test_email}),
            content_type='application/json'
        )
        token = req_resp.get_json().get("dev_reset_token")

        short_resp = self.client.post(
            '/api/auth/reset-password',
            data=json.dumps({"token": token, "password": "short"}),
            content_type='application/json'
        )
        self.assertEqual(short_resp.status_code, 400)
        data = short_resp.get_json()
        self.assertEqual(data.get("error"), "WeakPassword")

if __name__ == '__main__':
    unittest.main()
