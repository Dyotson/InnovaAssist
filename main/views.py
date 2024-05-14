from django.http import HttpResponse
from django.template import loader
from .forms import AlumnoForm
from .models import Alumno
from itertools import combinations
from rut_chile import rut_chile
import csv


# Create your views here.
def index(request):
    template = loader.get_template("index.html")
    form = AlumnoForm()
    if request.method == "POST":
        form = AlumnoForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data["rut"]
            form = AlumnoForm()
            all_subs = [rut[i:j] for i, j in combinations(range(len(rut) + 1), 2)]
            # Delete all_subs that have len not equal to 12
            all_subs = [sub for sub in all_subs if len(sub) == 9]
            # Check if all_subs contains a valid RUT
            if not any(rut_chile.is_valid_rut(sub) for sub in all_subs):
                result = f"RUT {rut} no es válido"
                return HttpResponse(
                    template.render({"form": form, "result": result}, request)
                )
            # Get the valid RUT
            rut = next(sub for sub in all_subs if rut_chile.is_valid_rut(sub))
            # Check if the RUT already exists
            if Alumno.objects.filter(rut=rut).exists():
                result = f"Alumno {rut} ya existe"
                return HttpResponse(
                    template.render({"form": form, "result": result}, request)
                )
            # Create the Alumno
            alumno = Alumno.objects.create(rut=rut)
            result = f"Alumno {rut} creado correctamente"
            return HttpResponse(
                template.render({"form": form, "result": result}, request)
            )
    return HttpResponse(template.render({"form": form}, request))


# Make view to export all almunos to a CSV file
def export_alumnos(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="alumnos.csv"'
    alumnos = Alumno.objects.all()
    writer = csv.writer(response)
    writer.writerow(["RUT"])
    for alumno in alumnos:
        writer.writerow([alumno.rut])
    return response


# Make a view to delete all alumnos
def delete_alumnos(request):
    Alumno.objects.all().delete()
    return HttpResponse("Alumnos eliminados correctamente")
