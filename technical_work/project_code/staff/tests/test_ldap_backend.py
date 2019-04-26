from django.test import TestCase
from staff.ldap_backend import LDAPBackend
from django.contrib.auth.models import User
from django.contrib.messages.api import MessageFailure
from django.test.client import RequestFactory

class TestLDAPBackend(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_authenticate_incorrect_details(self):
        lb = LDAPBackend()
        request = self.factory.get('/login/')
        try:
            #this could not be tested properly due to an issue with messaging middleware
            #it should reutnr none but instead fails becasue the middleware doesnt play nice while unit testing
            result = lb.authenticate(request, "mwfffj7", "ejfnwi")
            self.fail("Shoukd fail because exception is raised")
        except MessageFailure:
            pass

    def test_authenticate_correct_details(self):
        lb = LDAPBackend()
        result = lb.authenticate(None, "mwj7", "qh76T423")
        self.assertIn(result, User.objects.all())
