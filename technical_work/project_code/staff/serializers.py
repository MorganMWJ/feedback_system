from rest_framework import serializers
from staff.models import Lecture, Session, Question, Feedback
from staff.templatetags.format_extras import runtime_format

class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    runtime = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = '__all__'

    def get_start_time(self, obj):
        try:
            return obj.start_time.strftime('%d %b, %Y - %I:%M %p')
        except AttributeError:
            return ""

    def get_end_time(self, obj):
        try:
            return obj.end_time.strftime('%d %b, %Y - %I:%M %p')
        except AttributeError:
            return ""

    def get_runtime(self, obj):
        return runtime_format(obj.get_runtime())

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = (id)

    def get_feedback(self, obj):#todo
        return obj.get_feedback_summary()
