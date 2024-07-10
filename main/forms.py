from django import forms
from .models import Alumno


class AlumnoForm(forms.ModelForm):
    code = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Codigo", "autofocus": True}),
    )

    class Meta:
        model = Alumno
        fields = ["code"]
