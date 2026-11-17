import unittest
import secrets
from datetime import date, timedelta
from app import app, db_session
from models import User, Admin, EwasteItem, CollectionRequest, RecyclingCentre

class EWasteSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def tearDown(self):
        db_session.remove()

    def test_01_public_pages(self):
        # 1. Homepage
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Smart E-Waste Collection Drive', resp.data)

        # 2. About page
        resp = self.client.get('/about')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'About the E-Waste Management System', resp.data)

        # 3. Collection Centres page
        resp = self.client.get('/centres')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Authorized E-Waste Collection', resp.data)

        # 4. Proper Guidance page
        resp = self.client.get('/guidelines')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Proper E-Waste Disposal & Safe Storage Guidelines', resp.data)

        # 5. Awareness page
        resp = self.client.get('/awareness')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Public Environmental Awareness on E-Waste', resp.data)

        # 6. Quiz page
        resp = self.client.get('/quiz')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Eco Quiz', resp.data)

    def test_02_multi_user_registration_and_independent_login(self):
        """Test registration with at least three different email addresses and verify all three can log in independently."""
        unique_suffix = secrets.token_hex(3)
        users_to_test = [
            {
                'full_name': 'Arjun Kumar',
                'email': f'arjun_{unique_suffix}@techcorp.in',
                'phone': '+91 98450 11001',
                'password': 'passwordArjun123',
                'city': 'Bengaluru',
                'pincode': '560001'
            },
            {
                'full_name': 'Priya Sharma',
                'email': f'priya_{unique_suffix}@greenearth.org',
                'phone': '+91 98450 22002',
                'password': 'passwordPriya456',
                'city': 'Mysuru',
                'pincode': '570001'
            },
            {
                'full_name': 'Kiran Rao',
                'email': f'kiran_{unique_suffix}@ecoverse.com',
                'phone': '+91 98450 33003',
                'password': 'passwordKiran789',
                'city': 'Hubballi',
                'pincode': '580020'
            }
        ]

        # 1. Register all three distinct users
        for u in users_to_test:
            reg_resp = self.client.post('/register', data={
                'full_name': u['full_name'],
                'email': u['email'],
                'phone': u['phone'],
                'password': u['password'],
                'confirm_password': u['password'],
                'address': f"No. 12, Main Road, {u['city']}",
                'city': u['city'],
                'pincode': u['pincode']
            }, follow_redirects=True)
            self.assertEqual(reg_resp.status_code, 200)
            self.assertIn(b'Registration successful', reg_resp.data)

            # Verify user exists in database and password is encrypted/hashed
            db_user = db_session.query(User).filter_by(email=u['email']).first()
            self.assertIsNotNone(db_user, f"User {u['email']} was not saved in MySQL.")
            self.assertEqual(db_user.full_name, u['full_name'])
            self.assertNotEqual(db_user.password_hash, u['password'], "Password must never be stored in plain text.")
            self.assertTrue(db_user.password_hash.startswith('scrypt:') or db_user.password_hash.startswith('pbkdf2:'))

        # 2. Test duplicate email registration displays exact requirement message:
        # "Email already exists. Please login."
        dup_resp = self.client.post('/register', data={
            'full_name': 'Duplicate User',
            'email': users_to_test[0]['email'],
            'phone': '+91 99999 00000',
            'password': 'somePassword123',
            'confirm_password': 'somePassword123',
            'address': 'Some Address',
            'city': 'Bengaluru',
            'pincode': '560001'
        }, follow_redirects=True)
        self.assertIn(b'Email already exists. Please login.', dup_resp.data)

        # 3. Test independent login for all three users
        for u in users_to_test:
            user_client = app.test_client()
            login_resp = user_client.post('/login', data={
                'email': u['email'],
                'password': u['password']
            }, follow_redirects=True)
            self.assertEqual(login_resp.status_code, 200)
            self.assertIn(f"Welcome back, {u['full_name']}!".encode(), login_resp.data)

            # Dashboard shows user's name
            dash_resp = user_client.get('/dashboard')
            self.assertEqual(dash_resp.status_code, 200)
            self.assertIn(u['full_name'].encode(), dash_resp.data)

            # Logout
            logout_resp = user_client.get('/logout', follow_redirects=True)
            self.assertIn(b'You have been logged out successfully', logout_resp.data)

    def test_03_dashboard_user_isolation(self):
        """Verify each user can only see and manage their own e-waste records."""
        unique_suffix = secrets.token_hex(3)
        user_a_email = f"user_a_{unique_suffix}@example.com"
        user_b_email = f"user_b_{unique_suffix}@example.com"

        # Register User A
        self.client.post('/register', data={
            'full_name': 'User Alpha',
            'email': user_a_email,
            'phone': '+91 98450 11111',
            'password': 'password123',
            'confirm_password': 'password123',
            'city': 'Bengaluru'
        }, follow_redirects=True)

        # Register User B
        self.client.post('/register', data={
            'full_name': 'User Beta',
            'email': user_b_email,
            'phone': '+91 98450 22222',
            'password': 'password123',
            'confirm_password': 'password123',
            'city': 'Bengaluru'
        }, follow_redirects=True)

        # Client A logs in and registers an item
        client_a = app.test_client()
        item_a_name = f"Alpha Secret Laptop {unique_suffix}"
        client_a.post('/login', data={'email': user_a_email, 'password': 'password123'}, follow_redirects=True)
        client_a.post('/ewaste/register', data={
            'category': 'Laptops',
            'item_name': item_a_name,
            'quantity': '1',
            'item_condition': 'Working',
            'description': 'Dell Latitude E7470',
            'location': 'Bengaluru'
        }, follow_redirects=True)

        # User A sees item in their items
        items_a = client_a.get('/ewaste/my-items')
        self.assertIn(item_a_name.encode(), items_a.data)

        # Client B logs in with their own isolated session
        client_b = app.test_client()
        client_b.post('/login', data={'email': user_b_email, 'password': 'password123'}, follow_redirects=True)
        dash_b = client_b.get('/dashboard')
        self.assertNotIn(item_a_name.encode(), dash_b.data)
        items_b = client_b.get('/ewaste/my-items')
        self.assertNotIn(item_a_name.encode(), items_b.data)

    def test_04_forgot_and_reset_password_flow(self):
        """Test password recovery request and reset workflow."""
        unique_suffix = secrets.token_hex(3)
        user_email = f"reset_test_{unique_suffix}@example.com"
        initial_password = "initialPassword123"
        new_password = "updatedSecurePassword456"

        # Register user
        self.client.post('/register', data={
            'full_name': 'Reset Test User',
            'email': user_email,
            'phone': '+91 98450 33333',
            'password': initial_password,
            'confirm_password': initial_password,
            'city': 'Bengaluru'
        }, follow_redirects=True)

        # Request forgot password
        forgot_resp = self.client.post('/forgot-password', data={'email': user_email}, follow_redirects=True)
        self.assertEqual(forgot_resp.status_code, 200)
        self.assertIn(b'reset', forgot_resp.data.lower())

        # Check reset token generated in DB
        db_user = db_session.query(User).filter_by(email=user_email).first()
        self.assertIsNotNone(db_user.reset_token)
        self.assertIsNotNone(db_user.reset_token_expiry)
        token = db_user.reset_token

        # Reset password using token
        reset_resp = self.client.post(f'/reset-password/{token}', data={
            'password': new_password,
            'confirm_password': new_password
        }, follow_redirects=True)
        self.assertEqual(reset_resp.status_code, 200)
        self.assertIn(b'Your password has been reset successfully', reset_resp.data)

        # Verify old password fails
        fail_login = self.client.post('/login', data={'email': user_email, 'password': initial_password})
        self.assertIn(b'Invalid email or password', fail_login.data)

        # Verify new password succeeds
        success_login = self.client.post('/login', data={'email': user_email, 'password': new_password}, follow_redirects=True)
        self.assertIn(b'Welcome back, Reset Test User!', success_login.data)

    def test_05_authorized_centres_module(self):
        """Test authorized collection centres module with verified CPCB & KSPCB facilities."""
        # 1. Check all verified facilities are listed
        resp = self.client.get('/centres')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'M/s. E-Parisaraa Pvt. Ltd.', resp.data)
        self.assertIn(b'M/s. Sriram Eco Raksha Computer Services Pvt. Ltd.', resp.data)
        self.assertIn(b'M/s. 4R Recycling Pvt. Ltd.', resp.data)
        self.assertIn(b'M/s. Saahas Zero Waste', resp.data)
        self.assertIn(b'M/s. Sheeltron Digital Systems Pvt. Ltd.', resp.data)

        # 2. Verify dummy records are absent
        self.assertNotIn(b'Green Valley Community E-Waste Kiosk', resp.data)

        # 3. Search by city (Nelamangala)
        nel_resp = self.client.get('/centres?city=Nelamangala')
        self.assertEqual(nel_resp.status_code, 200)
        self.assertIn(b'E-Parisaraa', nel_resp.data)
        self.assertNotIn(b'Bommasandra', nel_resp.data)

        # 4. Search by district (Bengaluru Rural)
        dist_resp = self.client.get('/centres?district=Bengaluru+Rural')
        self.assertEqual(dist_resp.status_code, 200)
        self.assertIn(b'Nelamangala', dist_resp.data)
        self.assertIn(b'Hoskote', dist_resp.data)

        # 5. Search by PIN code (560058 - Peenya)
        pin_resp = self.client.get('/centres?pincode=560058')
        self.assertEqual(pin_resp.status_code, 200)
        self.assertIn(b'4R Recycling', pin_resp.data)
        self.assertIn(b'Cerebra Integrated', pin_resp.data)

        # 6. Filter by Facility Type
        rec_resp = self.client.get('/centres?facility_type=Authorized+Recycler')
        self.assertEqual(rec_resp.status_code, 200)
        self.assertIn(b'M/s. E-Parisaraa Pvt. Ltd.', rec_resp.data)
        self.assertNotIn(b'M/s. Sheeltron Digital Systems', rec_resp.data)

        dism_resp = self.client.get('/centres?facility_type=Authorized+Dismantler')
        self.assertEqual(dism_resp.status_code, 200)
        self.assertIn(b'M/s. 4R Recycling Pvt. Ltd.', dism_resp.data)
        self.assertNotIn(b'M/s. E-Parisaraa Pvt. Ltd.', dism_resp.data)

        # 7. Verify missing contact details display 'Contact details not available'
        self.assertIn(b'Contact details not available', resp.data)

        # 8. Verify Google Maps link is available for verified facilities
        self.assertIn(b'Get Directions (Google Maps)', resp.data)

    def test_06_admin_access_control(self):
        """Verify normal users cannot access admin pages."""
        # Unauthenticated request to /admin/centres redirects to admin login
        admin_resp = self.client.get('/admin/centres', follow_redirects=True)
        self.assertIn(b'Administrator Portal', admin_resp.data)

        # Normal user logged in trying to access admin
        unique_suffix = secrets.token_hex(2)
        norm_email = f"normal_{unique_suffix}@user.com"
        self.client.post('/register', data={
            'full_name': 'Normal User',
            'email': norm_email,
            'phone': '+91 98450 99999',
            'password': 'normalPassword123',
            'confirm_password': 'normalPassword123',
            'city': 'Bengaluru'
        })
        user_client = app.test_client()
        user_client.post('/login', data={'email': norm_email, 'password': 'normalPassword123'}, follow_redirects=True)
        # Try accessing admin users
        resp = user_client.get('/admin/users', follow_redirects=True)
        self.assertIn(b'Administrator Portal', resp.data)
        self.assertNotIn(b'Registered Citizens Directory', resp.data)

if __name__ == '__main__':
    unittest.main()
