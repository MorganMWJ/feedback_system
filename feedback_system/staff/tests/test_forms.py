from django.test import TestCase
from staff.forms import LoginForm

class TestForms(TestCase):
    #Login Form Tests
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
