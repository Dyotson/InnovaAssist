from django import forms
from .models import Alumno


class AlumnoForm(forms.ModelForm):
    rut = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "RUT", "autofocus": True}),
    )

    class Meta:
        model = Alumno
        fields = ["rut"]
