from django.test import TestCase
from django.utils import timezone
from student_feedback.models import Lecture, Question

# Create your tests here.
class LectureModelTests(TestCase):
    def test_is_currently_on_with_current_lecture(self):
        """
        is_currently_on() should return true for lectures
        with a start time earlier than now and an end time later than now
        """
        start = timezone.now() - timezone.timedelta(minutes=30)
        end = timezone.now() + timezone.timedelta(minutes=30)
        current_lecture = Lecture(lecture_title="My Lecture",
            start_time=start, end_time=end)

        self.assertIs(current_lecture.is_currently_on(), True)

    def test_is_currently_on_with_finished_lecture(self):
        """
        is_currently_on() should return false for lectures
        with a end time earlier than now
        """
        start = timezone.now() - timezone.timedelta(hours=2)
        end = timezone.now() - timezone.timedelta(hours=1)
        finished_lecture = Lecture(lecture_title="My Lecture",
            start_time=start, end_time=end)
        self.assertIs(finished_lecture.is_currently_on(), False)
