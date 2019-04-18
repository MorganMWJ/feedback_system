from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from staff.models import Lecture, Session, Time
from django.contrib.auth.models import User

class TestLectureModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="qn4g", password="telecom")

    def test_get_last_active_date_currently_running(self):
        newLecture = Lecture.objects.create(title="test", slide_count=4, user=self.user)
        earliestTime = (timezone.now()-timedelta(days=30))
        session = newLecture.session_set.create(code='XXX123')
        session.time_set.create(start=timezone.now())
        self.assertEqual(newLecture.get_last_active_date(), timezone.now())

    def test__str__(self):
        newLecture = Lecture.objects.create(title="My Lecture", slide_count=4, user=self.user)
        self.assertEqual(str(newLecture), "My Lecture")

class TestSessionModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="qn4g", password="telecom")
        self.lecture = Lecture.objects.create(title="test", slide_count=4, user=self.user)

    def test_merge_session_with_previous_session(self):
        session_1 = self.lecture.session_set.create(code="ABC123")
        session_1_start = timezone.now()-timedelta(days=3)
        session_1_end = timezone.now()-timedelta(days=2)
        session_1.time_set.create(start=session_1_start, end=session_1_end)
        session_2 = self.lecture.session_set.create(code="123ABC")
        session_2_start = timezone.now()-timedelta(days=1)
        session_2_end = timezone.now()
        session_2.time_set.create(start=session_2_start, end=session_2_end)

        session_2.merge('previous')

        self.assertEqual(self.lecture.session_set.count(), 1)
        result_session = self.lecture.session_set.all().first()
        self.assertEqual(result_session.code, "123ABC")
        self.assertEqual(result_session.time_set.count(), 2)
        self.assertEqual(result_session.time_set.all().first().start, session_1_start)
        self.assertEqual(result_session.time_set.all().first().end, session_1_end)
        self.assertEqual(result_session.time_set.all().last().start, session_2_start)
        self.assertEqual(result_session.time_set.all().last().end, session_2_end)
        self.assertEqual(result_session.get_total_runtime(), session_1.get_total_runtime()+session_2.get_total_runtime())


    def test_merge_session_with_next_session(self):
        session_1 = self.lecture.session_set.create(code="ABC123")
        session_1_start = timezone.now()-timedelta(days=3)
        session_1_end = timezone.now()-timedelta(days=2)
        session_1.time_set.create(start=session_1_start, end=session_1_end)
        session_2 = self.lecture.session_set.create(code="123ABC")
        session_2_start = timezone.now()-timedelta(days=1)
        session_2_end = timezone.now()
        session_2.time_set.create(start=session_2_start, end=session_2_end)

        session_1.merge('next')

        self.assertEqual(self.lecture.session_set.count(), 1)
        result_session = self.lecture.session_set.all().first()
        self.assertEqual(result_session.code, "ABC123")
        self.assertEqual(result_session.time_set.count(), 2)
        self.assertEqual(result_session.time_set.all().first().start, session_1_start)
        self.assertEqual(result_session.time_set.all().first().end, session_1_end)
        self.assertEqual(result_session.time_set.all().last().start, session_2_start)
        self.assertEqual(result_session.time_set.all().last().end, session_2_end)
        self.assertEqual(result_session.get_total_runtime(), session_1.get_total_runtime()+session_2.get_total_runtime())

    def test_merge_session_with_only_one_session(self):
        session_1 = self.lecture.session_set.create(code="ABC123")
        session_1_start = timezone.now()-timedelta(days=3)
        session_1_end = timezone.now()-timedelta(days=2)
        session_1.time_set.create(start=session_1_start, end=session_1_end)
        try:
            session_1.merge('next')
            session_1.merge('previous')
            self.fail("There is only one session therefore merge should have raised an exception")
        except Exception:
            pass

    def test_merge_session_with_previous_session_when_there_is_no_previous_session(self):
        session_1 = self.lecture.session_set.create(code="ABC123")
        session_1_start = timezone.now()-timedelta(days=3)
        session_1_end = timezone.now()-timedelta(days=2)
        session_1.time_set.create(start=session_1_start, end=session_1_end)
        session_2 = self.lecture.session_set.create(code="123ABC")
        session_2_start = timezone.now()-timedelta(days=1)
        session_2_end = timezone.now()
        session_2.time_set.create(start=session_2_start, end=session_2_end)

        try:
            session_1.merge('previous')
            self.fail("There is no previous session therefore merge should have raised an exception")
        except Exception:
            pass

    def test_merge_session_with_next_session_when_there_is_no_next_session(self):
        session_1 = self.lecture.session_set.create(code="ABC123")
        session_1_start = timezone.now()-timedelta(days=3)
        session_1_end = timezone.now()-timedelta(days=2)
        session_1.time_set.create(start=session_1_start, end=session_1_end)
        session_2 = self.lecture.session_set.create(code="123ABC")
        session_2_start = timezone.now()-timedelta(days=1)
        session_2_end = timezone.now()
        session_2.time_set.create(start=session_2_start, end=session_2_end)

        try:
            session_2.merge('next')
            self.fail("There is no next session therefore merge should have raised an exception")
        except Exception:
            pass

    def test_get_total_runtime_session_with_no_times(self):
        session = self.lecture.session_set.create(code="123123")
        self.assertEqual(session.get_total_runtime(), 0)


class TestTimeModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="qn4g", password="telecom")
        self.lecture = Lecture.objects.create(title="test", slide_count=4, user=self.user)
        self.session = Session.objects.create(code="123123", lecture=self.lecture)

    def test_get_runtime_of_running_time(self):
        start_time = timezone.now()-timedelta(days=3)
        time = self.session.time_set.create(start=start_time)

        self.assertEqual(time.get_runtime(), timezone.now()-start_time)

    def test_get_runtime_of_finished_time(self):
        start_time = timezone.now()-timedelta(days=3)
        end_time = timezone.now()-timedelta(days=2)
        time = self.session.time_set.create(start=start_time, end=end_time)

        self.assertEqual(time.get_runtime(), end_time-start_time)
