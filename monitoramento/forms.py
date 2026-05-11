from django import forms

from .models import Analise


class AnaliseForm(forms.ModelForm):

    class Meta:

        model = Analise

        fields = '__all__'