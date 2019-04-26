from django.test import TestCase
from django.test import Client
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import RequestFactory
from staff.models import Lecture, Session
from django.core.files import File
# import pdb

class TestLoginView(TestCase):
    def setUp(self):
        pass

    def test_view_url_exists_at_desired_location_en(self):
        response = self.client.get('/en/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_at_desired_location_cy(self):
        response = self.client.get('/cy/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('staff:login'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('staff:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/login.html')

    def test_view_post_with_invalid_data(self):
        response = self.client.post(reverse('staff:login'), {'wrong' : 'foobar'})
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid form data')

    def test_view_post_with_valid_login(self):
        response = self.client.post(reverse('staff:login'), {'uid' : 'mwj7', 'pswd': 'qh76T423'})
        self.assertRedirects(response, reverse('staff:lecture_list'))

    def test_view_post_with_valid_login_successful_redirect_to_next(self):
        response = self.client.post(reverse('staff:login'), {'uid': 'mwj7', 'pswd': 'qh76T423', 'next': '/en/lecture/new/'})
        self.assertRedirects(response, reverse('staff:lecture_create'))

class TestLogoutView(TestCase):
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('staff:logout'))
        self.assertRedirects(response, reverse('staff:login'))

class TestLectureListView(TestCase):

    @classmethod
    def setUpTestData(cls):
        number_of_lectures = 13

        test_user1 = User.objects.create_user(username='mwj7', password='qh76T423')
        test_user1.save()

        #add the 13 lectures
        for lecture_id in range(number_of_lectures):
            Lecture.objects.create(
                title=f'Lecture {lecture_id}',
                slide_count=3,
                user = test_user1
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff:lecture_list'))
        self.assertRedirects(response, '/login/?next=/en/lectures/', status_code=302, target_status_code=302)

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_list'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'mwj7')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'staff/lecture_list.html')

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get('/en/lectures/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_list'))
        self.assertEqual(response.status_code, 200)

    def test_pagination_is_eight(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['object_list']) == 8)

    def test_lists_all_authors(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        # Get second page and confirm it has (exactly) remaining 5 items
        response = self.client.get(reverse('staff:lecture_list')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['object_list']), 5)

    def test_search_lecture_by_name(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_list')+'?q=Lecture 2')
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(response.context['object_list'][0].title, 'Lecture 2')

class TestLectureDetailView(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='mwj7', password='qh76T423')
        test_user1.save()

        self.lecture = Lecture.objects.create(
            title='Lecture 1',
            slide_count=3,
            user = test_user1
        )

        self.lecture.session_set.create(code="QWE123")
        self.lecture.session_set.create(code="UYT65R")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff:lecture_detail', kwargs={'pk': self.lecture.id}), follow=True)
        #unsure what is going on here with the %2F
        self.assertRedirects(response, '/en/login/?next=%2Fen%2Flecture%2F'+str(self.lecture.id)+'%2F')


    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_detail', kwargs={'pk': self.lecture.id}))
        self.assertEqual(response.status_code, 200)


    def test_sessions_are_listed(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_detail', kwargs={'pk': self.lecture.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('sessions' in response.context)
        self.assertEqual(len(response.context['sessions']),2)

class TestLectureDeleteView(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='mwj7', password='qh76T423')
        test_user1.save()
        self.test_user = test_user1

        self.lecture = Lecture.objects.create(
            title='Lecture 1',
            slide_count=3,
            user = test_user1
        )

    def tearDown(self):
        try:
            Lecture.objects.get(pk=self.lecture.id).delete()
        except Lecture.DoesNotExist:
            pass #lecture is already deleted
        User.objects.get(pk=self.test_user.id).delete()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff:lecture_delete', kwargs={'pk': self.lecture.id}))
        self.assertRedirects(response, '/login/?next=/en/lecture/'+str(self.lecture.id)+'/delete/', status_code=302, target_status_code=302)


    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_delete', kwargs={'pk': self.lecture.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/lecture_confirm_delete.html')

    def test_lecture_gets_deleted(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.post(reverse('staff:lecture_delete', kwargs={'pk': self.lecture.id}))
        self.assertEqual(len(Lecture.objects.all()),0)

    def test_redirect_after_delete(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.post(reverse('staff:lecture_delete', kwargs={'pk': self.lecture.id}), follow=True)
        self.assertRedirects(response, reverse('staff:lecture_list'), status_code=302, target_status_code=200)

class TestLectureCreateView(TestCase):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff:lecture_create'), follow=True)
        self.assertRedirects(response, '/en/login/?next=%2Fen%2Flecture%2Fnew%2F')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_create'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_create'))
        self.assertTemplateUsed(response, 'staff/lecture_new.html')

    def test_view_post_with_invalid_data(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.post(reverse('staff:lecture_create'), {'wrong' : 'foobar'})
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid form data')

    def test_view_with_valid_data_for_creating_lecture(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        title = 'My Lecture'
        slide_count = 3
        notes = 'Awesome notes'
        response = self.client.post(reverse('staff:lecture_create'), {'title' : title, 'slide_count': slide_count, 'notes': notes})
        new_lecture = Lecture.objects.all()[0]
        self.assertEqual(new_lecture.title, title)
        self.assertEqual(new_lecture.slide_count, slide_count)
        self.assertEqual(new_lecture.notes, notes)

    def test_view_with_valid_data_for_creating_lecture_including_pdf_file(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        title = 'My Lecture'
        slide_count = 3
        notes = 'Awesome notes'
        with open('assets/test_lecture.pdf', 'rb') as fp:
            self.client.post(reverse('staff:lecture_create'), {'title' : title, 'slide_count': slide_count, 'notes': notes, 'file': fp})
        new_lecture = Lecture.objects.all()[0]
        self.assertEqual(new_lecture.title, title)
        self.assertEqual(new_lecture.slide_count, slide_count)
        self.assertEqual(new_lecture.notes, notes)
        import filecmp
        filecmp.cmp('assets/test_lecture.pdf', new_lecture.file.path)

class TestLectureUpdateView(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='mwj7', password='qh76T423')
        test_user1.save()
        self.test_user = test_user1

        self.lecture = Lecture.objects.create(
            title='Lecture 1',
            slide_count=3,
            user = test_user1
        )

    def tearDown(self):
        Lecture.objects.get(pk=self.lecture.id).delete()
        User.objects.get(pk=self.test_user.id).delete()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff:lecture_update', kwargs={'pk': self.lecture.id}), follow=True)
        self.assertRedirects(response, '/en/login/?next=%2Fen%2Flecture%2F'+ str(self.lecture.id) +'%2Fedit%2F')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_update', kwargs={'pk': self.lecture.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_update', kwargs={'pk': self.lecture.id}))
        self.assertTemplateUsed(response, 'staff/lecture_edit.html')

    def test_view_post_with_invalid_data(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.post(reverse('staff:lecture_update', kwargs={'pk': self.lecture.id}), {'wrong' : 'foobar'}, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid form data')

    def test_view_with_valid_data_for_updating_lecture(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        title = 'My Lecture'
        slide_count = 3
        notes = 'Awesome notes'
        response = self.client.post(reverse('staff:lecture_update', kwargs={'pk': self.lecture.id}), {'title' : title, 'slide_count': slide_count, 'notes': notes})
        updated_lecture = Lecture.objects.all()[0]
        self.assertEqual(updated_lecture.title, title)
        self.assertEqual(updated_lecture.slide_count, slide_count)
        self.assertEqual(updated_lecture.notes, notes)

    def test_view_with_valid_data_for_updating_lecture_including_pdf_file(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        title = 'My Lecture'
        slide_count = 3
        notes = 'Awesome notes'
        with open('assets/test_lecture.pdf', 'rb') as fp:
            self.client.post(reverse('staff:lecture_update', kwargs={'pk': self.lecture.id}), {'title' : title, 'slide_count': slide_count, 'notes': notes, 'file': fp})
        updated_lecture = Lecture.objects.all()[0]
        self.assertEqual(updated_lecture.title, title)
        self.assertEqual(updated_lecture.slide_count, slide_count)
        self.assertEqual(updated_lecture.notes, notes)
        import filecmp
        filecmp.cmp('assets/test_lecture.pdf', updated_lecture.file.path)


class TestExtractFromPdfView(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='mwj7', password='qh76T423')
        test_user1.save()
        self.test_user = test_user1

        self.lecture = Lecture.objects.create(
            title='Lecture 1',
            slide_count=3,
            user = test_user1
        )
        f = open('assets/test_lecture.pdf')
        self.lecture.file.save("test_lecture_file", File(f))

    def tearDown(self):
        Lecture.objects.get(pk=self.lecture.id).delete()
        User.objects.get(pk=self.test_user.id).delete()

    def test_must_own_target_object(self):
        pass

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff:lecture_extarct', kwargs={'pk': self.lecture.id}), follow=True)
        self.assertRedirects(response, '/en/login/?next=%2Fen%2Flecture%2F'+ str(self.lecture.id) +'%2Fextract%2F')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='mwj7', password='qh76T423')
        response = self.client.get(reverse('staff:lecture_extarct', kwargs={'pk': self.lecture.id}))
        self.assertEqual(response.status_code, 200)

class TestLectureFileView(TestCase):
    pass

class TestSessionNewView(TestCase):
    pass

class TestSessionStartView(TestCase):
    pass

class TestSessionStopView(TestCase):
    pass

class TestSessionDeleteView(TestCase):
    pass

class TestSessionMergePrevious(TestCase):
    pass

class TestSessionMergeNext(TestCase):
    pass

class TestSessionRegenerateCodeView(TestCase):
    pass

class TestSessionToggleQuestionsView(TestCase):
    pass

class TestSessionQuestionsView(TestCase):
    pass

class TestLectureSessionsView(TestCase):
    pass

class TestQuestionMarkReviewedView(TestCase):
    pass

class TestConnectView(TestCase):
    pass

class TestDisconnectView(TestCase):
    pass

class TestFeedbackView(TestCase):
    pass

class TestFeedbackCreateView(TestCase):
    pass

class TestQuestionCreateView(TestCase):
    pass

class TestQuestionDeleteView(TestCase):
    pass

class TestFeedbackDetailView(TestCase):
    pass

class TestSessionFeedbackChartDataView(TestCase):
    pass
