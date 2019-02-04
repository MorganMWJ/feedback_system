from django.test import TestCase
from django.utils import timezone
from student_feedback.models import Lecture, Question

# Create your tests here.
class LectureModelTests(TestCase):
    def test_is_currently_on_with_current_lecture(self):
        """
        is_currently_on() should return true for lectures
        with a start time before now and a end time after now
        """
        start = timezone.now() - timezone.timedelta(minutes=30)
        end = timezone.now() + timezone.timedelta(minutes=30)
        current_lecture = Lecture(lecture_title="My Lecture",
            start_time=start, end_time=end)

        self.assertIs(current_lecture.is_currently_on(), True)
