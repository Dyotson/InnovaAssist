from django.http import HttpResponse
from django.template import loader
from .forms import AlumnoForm
from .models import Alumno
import csv
import tempfile
import os
from django.http import HttpRequest
from django.shortcuts import redirect
from datetime import datetime
import pyminizip
import io


# Create your views here.
def index(request: HttpRequest):
    template = loader.get_template("index.html")
    form = AlumnoForm()
    if request.method == "POST":
        form = AlumnoForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            form = AlumnoForm()
            # Check if the RUT already exists
            if Alumno.objects.filter(code=code).exists():
                user = Alumno.objects.get(code=code)
                user.count += 1
                user.save()
                result = f"Caja agregada correctamente a persona {code}"
                return HttpResponse(
                    template.render({"form": form, "result": result}, request)
                )
            # Create the Alumno
            user = Alumno.objects.create(code=code)
            result = f"Persona {code} creado correctamente"
            return HttpResponse(
                template.render({"form": form, "result": result}, request)
            )
    return HttpResponse(template.render({"form": form}, request))


# Make view to export all almunos to a CSV file thgat contains the code and count
def export_alumnos(request: HttpRequest):
    # Create the CSV file in memory
    csv_file = io.StringIO()
    writer = csv.writer(csv_file)

    if Alumno.objects.count() == 0:
        response = HttpResponse(content_type="text/plain")
        response.write("No data available.")
        return response

    first = Alumno.objects.all().order_by("created_at").first()
    first.created_at = first.created_at.astimezone()

    last = Alumno.objects.all().order_by("updated_at").last()
    last.updated_at = last.updated_at.astimezone()

    writer.writerow(
        ["Reporte de cajas", f"Desde {first.created_at} hasta {last.updated_at}"]
    )
    writer.writerow(["code", "count"])

    for alumno in Alumno.objects.all():
        writer.writerow([alumno.code, alumno.count])

    csv_file.seek(0)

    # Write the CSV content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
        temp_csv.write(csv_file.getvalue().encode("utf-8"))
        temp_csv_path = temp_csv.name

    # Create a temporary file for the ZIP output
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
        temp_zip_path = temp_zip.name

    password = "fru2024.."  # Set your desired password here

    # Compress the CSV file into the ZIP file with password
    pyminizip.compress(temp_csv_path, None, temp_zip_path, password, 5)

    # Read the ZIP file content
    with open(temp_zip_path, "rb") as zip_file:
        zip_content = zip_file.read()

    # Clean up the temporary files
    os.remove(temp_csv_path)
    os.remove(temp_zip_path)

    # Return the ZIP file as a response
    response = HttpResponse(zip_content, content_type="application/zip")
    response["Content-Disposition"] = (
        f'attachment; filename="Reporte_{datetime.now().date()}.zip"'
    )

    return response


# Make a view to delete all alumnos
def delete_alumnos(request: HttpRequest):
    if request.method == "POST":
        if "si" in request.POST:
            Alumno.objects.all().delete()
            template = loader.get_template("index.html")
            result = "El registo del día ha sido eliminado correctamente"
            return HttpResponse(
                template.render({"form": AlumnoForm(), "result": result}, request)
            )
        else:
            return redirect("index")
    else:
        template = loader.get_template("confirm.html")
        return HttpResponse(template.render({}, request))
