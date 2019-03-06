import datetime

from django.test import TestCase
from django.utils import timezone
from staff.models import Lecture, Session

class TestModels(TestCase):
    def test_get_first_started(self):
        newLecture = Lecture.objects.create(title="test", slide_count=4,
                        author_username='why6',
                        author_forename='fiona',
                        author_surname='wittenick',
                        session_code='RX4S32',
                        is_running=False)

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

        self.assertEqual(newLecture.getFirstStarted(), earliestTime)

    def test_get_total_runtime(self):
        newLecture = Lecture.objects.create(title="test", slide_count=4,
                        author_username='why6',
                        author_forename='fiona',
                        author_surname='wittenick',
                        session_code='RX4S32',
                        is_running=False)

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

        print(newLecture.getTotalRuntime())
