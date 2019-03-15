import datetime

from django.test import TestCase
from django.utils import timezone
from staff.models import Lecture, Session

class TestLectureModel(TestCase):
    def test_get_first_started(self):
        newLecture = Lecture.objects.create(title="test", slide_count=4,
                        author_username='why6',
                        author_forename='fiona',
                        author_surname='wittenick',
                        session_code='RX4S32',
                        is_running=False,
                        date_created=timezone.now())

        earliestTime = (timezone.now()-datetime.timedelta(days=30))
        newLecture.session_set.create(
                        start_time=earliestTime,
                        end_time=(timezone.now()-datetime.timedelta(days=29)))
        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=10)),
                        end_time=(timezone.now()-datetime.timedelta(days=10)))
        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=28)),
                        end_time=(timezone.now()-datetime.timedelta(days=27)))

        self.assertEqual(newLecture.get_first_started(), earliestTime)

    def test_get_last_ended(self):
        newLecture = Lecture.objects.create(title="test", slide_count=4,
                        author_username='why6',
                        author_forename='fiona',
                        author_surname='wittenick',
                        session_code='RX4S32',
                        is_running=False,
                        date_created=timezone.now())

        latestTime = (timezone.now()-datetime.timedelta(days=9))
        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=30)),
                        end_time=(timezone.now()-datetime.timedelta(days=29)))
        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=10)),
                        end_time=latestTime)
        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=28)),
                        end_time=(timezone.now()-datetime.timedelta(days=27)))

        self.assertEqual(newLecture.get_last_ended(), latestTime)

    def test_get_last_session(self):
        newLecture = Lecture.objects.create(title="test", slide_count=4,
                        author_username='why6',
                        author_forename='fiona',
                        author_surname='wittenick',
                        session_code='RX4S32',
                        is_running=False,
                        date_created=timezone.now())

        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=30)),
                        end_time=(timezone.now()-datetime.timedelta(days=29)))
        lastSession = newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=10)),
                        end_time=(timezone.now()-datetime.timedelta(days=9)))
        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=28)),
                        end_time=(timezone.now()-datetime.timedelta(days=27)))

        self.assertEqual(newLecture.get_last_session(), lastSession)

    def test_get_last_session_with_null_end_time(self):
        newLecture = Lecture.objects.create(title="test", slide_count=4,
                        author_username='why6',
                        author_forename='fiona',
                        author_surname='wittenick',
                        session_code='RX4S32',
                        is_running=False,
                        date_created=timezone.now())

        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=30)),
                        end_time=(timezone.now()-datetime.timedelta(days=29)))
        lastSession = newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=10)))
        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=28)),
                        end_time=(timezone.now()-datetime.timedelta(days=27)))

        self.assertEqual(newLecture.get_last_session(), lastSession)

    def test_get_total_runtime(self):
        newLecture = Lecture.objects.create(title="test", slide_count=4,
                        author_username='why6',
                        author_forename='fiona',
                        author_surname='wittenick',
                        session_code='RX4S32',
                        is_running=False,
                        date_created=timezone.now())

        earliestTime = (timezone.now()-datetime.timedelta(days=30))
        newLecture.session_set.create(
                        start_time=earliestTime,
                        end_time=(timezone.now()-datetime.timedelta(days=29)))
        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=10)),
                        end_time=(timezone.now()-datetime.timedelta(days=10)))
        newLecture.session_set.create(
                        start_time=(timezone.now()-datetime.timedelta(days=28)),
                        end_time=(timezone.now()-datetime.timedelta(days=27)))

        # print(newLecture.get_total_runtime())
    def test__str__(self):
        newLecture = Lecture.objects.create(title="My Lecture", slide_count=4,
                        author_username='why6',
                        author_forename='fiona',
                        author_surname='wittenick',
                        session_code='RX4S32',
                        is_running=False,
                        date_created=timezone.now())
        self.assertEqual(str(newLecture), "My Lecture")
