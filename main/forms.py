from django import forms
from .models import Alumno
import unicodedata


class AlumnoForm(forms.ModelForm):
    code = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Codigo", "autofocus": True}),
    )

    class Meta:
        model = Alumno
        fields = ["code"]

    def clean_code(self):
        code = self.cleaned_data.get("code", "")

        # Limpiar espacios al inicio y final
        code = code.strip()

        # Normalizar unicode para remover caracteres invisibles/combinados
        code = unicodedata.normalize("NFKC", code)

        # Remover caracteres de control y espacios adicionales
        code = "".join(
            char for char in code if not unicodedata.category(char).startswith("C")
        )

        # Limpiar espacios internos múltiples
        code = " ".join(code.split())

        return code
