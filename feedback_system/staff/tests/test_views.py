from django.test import TestCase
from django.test import Client
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse

import pdb

class TestViews(TestCase):
    def setUp(self):
        self.cli = Client()

    #debug
    def sessKeys(self):
        print(self.cli.session.keys())
        for key,value in self.cli.session.items():
            print(key + " => " + value)

    #Login View Tests
    def test_login_GET(self):
        response = self.cli.get(reverse('staff:login'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/login.html')

    def test_login_POST_correct_uid_and_pswd_posted(self):
        response = self.cli.post(reverse('staff:login'), {'uid': 'mwj7', 'pswd': 'qh76T423'})
        self.assertEquals(response.status_code, 302)
        self.assertIn('_auth_user_id', self.cli.session)
        user = User.objects.get(username="mwj7")
        self.assertEqual(int(self.cli.session['_auth_user_id']), user.pk)

    def test_login_POST_incorrect_uid_and_pswd_posted(self):
        response = self.cli.post(reverse('staff:login'), {'uid': 'WRONG', 'pswd': 'qh76T423'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['login_error'], True)
        self.assertNotIn('_auth_user_id', self.cli.session)
        with self.assertRaisesMessage(User.DoesNotExist, 'User matching query does not exist.'):
            User.objects.get(username="mwj7")

    def test_login_POST_invalid_form_data_missing_uid(self):
        response = self.cli.post(reverse('staff:login'), {'uid': '', 'pswd': 'qh76T423'})
        self.assertEquals(response.status_code, 200)
        #self.assertEquals(response.context['invalid_form_error'], True)
        self.assertNotIn('_auth_user_id', self.cli.session)

    def test_login_POST_invalid_form_data_missing_pswd(self):
        response = self.cli.post(reverse('staff:login'), {'uid': 'mwj8', 'pswd': ''})
        self.assertEquals(response.status_code, 200)
        #self.assertEquals(response.context['invalid_form_error'], True)
        self.assertNotIn('_auth_user_id', self.cli.session)

    #Logout View Tests
    def test_logout_GET(self):
        response = self.cli.get(reverse('staff:logout'))
        self.assertEquals(response.status_code, 302)

    #Index View Tests
    def test_index_redirect_if_not_logged_in(self):
        response = self.cli.get(reverse('staff:index'))
        self.assertRedirects(response, '/staff/login/?next=/staff/lectures/')
