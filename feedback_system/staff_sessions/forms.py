from django import forms

class LoginForm(forms.Form):
    uid = forms.CharField(label='Your Username', max_length=10, widget=forms.TextInput())
    pswd = forms.CharField(label="Your Password", widget=forms.PasswordInput())
    check = forms.BooleanField(label="Remember me")
