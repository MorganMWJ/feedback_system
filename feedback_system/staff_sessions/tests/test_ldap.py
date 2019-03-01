from django.test import TestCase
from staff_sessions.ldap_backend import LDAPBackend
from django.contrib.auth.models import User

class TestLDAPBackend(TestCase):
    def test_authenticate_incorrect_details(self):
        lb = LDAPBackend()
        result = lb.authenticate(None, "mwfffj7", "ejfnwi")
        self.assertEquals(result, None)

    def test_authenticate_correct_details(self):
        lb = LDAPBackend()
        result = lb.authenticate(None, "mwj7", "qh76T423")
        self.assertIn(result, User.objects.all())
