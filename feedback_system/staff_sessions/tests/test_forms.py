from django.test import TestCase
from staff_sessions.forms import LoginForm

class TestLoginForm(TestCase):
    def test_valid_login_form(self):
        data = {'uid': "mwj6", 'pswd': "12345678"}
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_login_form_no_uid(self):
        data = {'uid': "", 'pswd': "12345678"}
        form = LoginForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_login_form_no_pswd(self):
        data = {'uid': "mwj6", 'pswd': ""}
        form = LoginForm(data=data)
        self.assertFalse(form.is_valid())
