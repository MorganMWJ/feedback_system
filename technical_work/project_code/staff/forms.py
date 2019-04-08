from django import forms
from staff.models import Feedback, Lecture
from staff.validators import validate_file_extension
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters allowed.')

class LoginForm(forms.Form):
    uid = forms.CharField(label=_('Username'), max_length=10, widget=forms.TextInput(attrs={'placeholder': _("Your Username")}))
    pswd = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': _("Your Password")}))

class LectureDetailsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LectureDetailsForm, self).__init__(*args, **kwargs)
        self.fields['title'].max_length = 150
        self.fields['slide_count'].min_value = 1
        self.fields['notes'].required = False

    class Meta:
        model = Lecture
        fields = ['title', 'slide_count', 'notes']
        labels = {
            'title': _('Lecture/Workshop Title'),
            'slide_count': _('Number of Slides'),
            'notes': _('Extra Notes')
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _("Title here...")}),
            'slide_count': forms.NumberInput(attrs={'placeholder': _("Slide Count here...")}),
            'notes': forms.Textarea(attrs={'placeholder': _("Notes here...")})
        }

class PDFUploadForm(forms.Form):
    lecture_pdf_file = forms.FileField(required=False, validators=[validate_file_extension])

class ConnectForm(forms.Form):
    code = forms.CharField(label=_('Session Code'), min_length=6, max_length=6, validators=[alphanumeric], widget=forms.TextInput(attrs={'placeholder': _("Code here...")}))

class QuestionForm(forms.Form):
    question = forms.CharField(label=_('Ask a question?'), max_length=250, widget=forms.Textarea(attrs={'placeholder': _("Enter a question or comment")}))

class FeedbackForm(forms.ModelForm):

    def __init__(self, lecture, *args, **kwargs): #add in options to exclude!!??
        super(FeedbackForm, self).__init__(*args, **kwargs)
        #build list from number of lecture slides
        choice_list = [(x, 'Slide '+str(x)) for x in range(1,lecture.slide_count+1)]
        #add gneral option for not associating feedback with a specific slide
        choice_list.insert(0, (0,"Not Specified (General Feedback)"))
        self.fields['slide_number'] =  forms.ChoiceField(label=_('Feedback for which slide'), choices=choice_list)

    class Meta:
        model = Feedback
        fields = ['overall_feedback', 'delivery_speed', 'content_complexity', 'content_presentation', 'level_of_engagement', 'slide_number']
