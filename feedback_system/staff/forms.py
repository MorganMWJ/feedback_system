from django import forms
from staff.validators import validate_file_extension
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters allowed.')

class LoginForm(forms.Form):
    uid = forms.CharField(label=_('Username'), max_length=10, widget=forms.TextInput(attrs={'placeholder': _("Your Username")}))
    pswd = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': _("Your Password")}))

class NewLectureForm(forms.Form):
    title = forms.CharField(label=_('Lecture/Workshop Title'), max_length=150, widget=forms.TextInput(attrs={'placeholder': _("Title here...")}))
    slide_count = forms.IntegerField(label=_('Number of Slides'), min_value=1, widget=forms.NumberInput(attrs={'placeholder': _("Slide Count here...")}))
    notes = forms.CharField(label=_('Extra Notes'), required=False, widget=forms.Textarea(attrs={'placeholder': _("Notes here...")}))

class PDFUploadForm(forms.Form):
    lecture_pdf_file = forms.FileField(required=False, validators=[validate_file_extension])

class ConnectForm(forms.Form):
    code = forms.CharField(label=_('Session Code'), min_length=6, max_length=6, validators=[RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')], widget=forms.TextInput(attrs={'placeholder': _("Code here...")}))
