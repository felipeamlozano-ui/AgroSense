from django.contrib.auth.forms import AuthenticationForm
from django import forms

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input-login",
            "placeholder": "Digite seu email"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "input-login",
            "placeholder": "Digite sua senha"
        })
    )