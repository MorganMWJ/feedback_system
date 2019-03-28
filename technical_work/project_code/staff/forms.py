from django import forms
from staff.models import Feedback
from staff.validators import validate_file_extension
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters allowed.')

class LoginForm(forms.Form):
    uid = forms.CharField(label=_('Username'), max_length=10, widget=forms.TextInput(attrs={'placeholder': _("Your Username")}))
    pswd = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': _("Your Password")}))

class LectureDetailsForm(forms.Form):

    # def __init__(self, lecture, *args, **kwargs):
    #     super(LectureDetailsForm, self).__init__(*args, **kwargs)
    #     self.fields['title'] = forms.CharField(label=_('Lecture/Workshop Title'), max_length=150, widget=forms.TextInput(attrs={'placeholder': lecture.title}))
    #     self.fields['slide_count'] = forms.IntegerField(label=_('Number of Slides'), min_value=1, widget=forms.NumberInput(attrs={'placeholder': str(lecture.slide_count)}))
    #     self.fields['notes'] = forms.CharField(label=_('Extra Notes'), required=False, widget=forms.Textarea(attrs={'placeholder': lecture.notes}))

    title = forms.CharField(label=_('Lecture/Workshop Title'), max_length=150, widget=forms.TextInput(attrs={'placeholder': _("Title here...")}))
    slide_count = forms.IntegerField(label=_('Number of Slides'), min_value=1, widget=forms.NumberInput(attrs={'placeholder': _("Slide Count here...")}))
    notes = forms.CharField(label=_('Extra Notes'), required=False, widget=forms.Textarea(attrs={'placeholder': _("Notes here...")}))

class PDFUploadForm(forms.Form):
    lecture_pdf_file = forms.FileField(required=False, validators=[validate_file_extension])

class ConnectForm(forms.Form):
    code = forms.CharField(label=_('Session Code'), min_length=6, max_length=6, validators=[alphanumeric], widget=forms.TextInput(attrs={'placeholder': _("Code here...")}))

class QuestionForm(forms.Form):
    question = forms.CharField(label=_('Ask a question?'), max_length=250, widget=forms.Textarea(attrs={'placeholder': _("Enter a question or comment")}))

class FeedbackForm(forms.Form):

    def __init__(self, lecture, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields['slide_options'] = forms.ChoiceField(label=_('Feedback for which slide'), choices=[(x, x) for x in range(1,lecture.slide_count+1)])

    overall_option = forms.ChoiceField(label=_('Overall Feedback'), choices=Feedback.OVERALL_FEEDBACK_CHOICES)
    speed_options = forms.ChoiceField(label=_('Delivery Speed'), choices=Feedback.DELIVERY_SPEED_CHOICES)
    complexity_options = forms.ChoiceField(label=_('Content Complexity'), choices=Feedback.CONTENT_COMPLEXITY_CHOICES)
    presentation_options = forms.ChoiceField(label=_('Interest/Engagement'), choices=Feedback.CONTENT_PRESENTATION_CHOICES)
    engagment_options = forms.ChoiceField(label=_('Content Presentation'), choices=Feedback.LEVEL_OF_ENGAGMENT_CHOICES)
