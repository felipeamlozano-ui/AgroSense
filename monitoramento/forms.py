from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Analise  # Importe o seu modelo aqui
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm  # <-- O segredo está aqui!
from .models import Analise, Usuario

# ADICIONE ESTE FORMULÁRIO ABAIXO:
class AnaliseForm(forms.ModelForm):
    class Meta:
        model = Analise
        fields = ['cultura', 'umidade', 'ph', 'temperatura']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "input-login", "placeholder": "Digite seu email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "input-login", "placeholder": "Digite sua senha"}))

class AnaliseForm(forms.ModelForm):
    class Meta:
        model = Analise
        fields = ['cultura', 'umidade', 'ph', 'temperatura']

# ADICIONE ESTE FORMULÁRIO ABAIXO:
class CustomUserCreationForm(UserCreationForm):
    nome_completo = forms.CharField(widget=forms.TextInput(attrs={"class": "input-login", "placeholder": "Seu nome completo"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "input-login", "placeholder": "Seu melhor e-mail"}))
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "input-login", "placeholder": "Nome de usuário (ex: joao123)"}))

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('nome_completo', 'email', 'username')