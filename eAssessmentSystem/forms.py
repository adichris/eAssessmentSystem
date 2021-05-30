from django import forms


class StudentLoginForm(forms.Form):
    index_number = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
