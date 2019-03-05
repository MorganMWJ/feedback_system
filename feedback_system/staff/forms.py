from django import forms
from django.utils.translation import ugettext_lazy as _

class LoginForm(forms.Form):
    uid = forms.CharField(label=_('Username'), max_length=10, widget=forms.TextInput(attrs={'placeholder': _("Your Username")}))
    pswd = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': _("Your Password")}))

class NewLectureForm(forms.Form):
    title = forms.CharField(label=_('Lecture/Workshop Title'), max_length=50, widget=forms.TextInput(attrs={'placeholder': _("Title here...")}))
    slide_count = forms.IntegerField(label=_('Number of Slides'), min_value=1, widget=forms.NumberInput(attrs={'placeholder': _("Slide Count here...")}))
    notes = forms.CharField(label=_('Lecture/Workshop Title'), required=False, widget=forms.Textarea(attrs={'placeholder': _("Notes here...")}))
