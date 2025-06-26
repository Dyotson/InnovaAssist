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
import unicodedata
import logging

# Configurar logging para debug
logger = logging.getLogger(__name__)


def clean_barcode(code):
    """
    Limpia el código de barras de espacios, caracteres unicode invisibles
    y otros caracteres problemáticos que pueden venir de pistolas lectoras.
    """
    if not code:
        return code

    # Limpiar espacios al inicio y final
    code = code.strip()

    # Normalizar unicode para remover caracteres invisibles/combinados
    code = unicodedata.normalize("NFKC", code)

    # Remover caracteres de control (incluyendo caracteres invisibles)
    code = "".join(
        char for char in code if not unicodedata.category(char).startswith("C")
    )

    # Limpiar espacios internos múltiples
    code = " ".join(code.split())

    return code


# Create your views here.
def index(request: HttpRequest):
    template = loader.get_template("index.html")
    form = AlumnoForm()
    if request.method == "POST":
        form = AlumnoForm(request.POST)
        if form.is_valid():
            raw_code = form.cleaned_data["code"]

            # Aplicar limpieza adicional al código (doble verificación)
            code = clean_barcode(raw_code)

            # Log para debug - nos ayudará a detectar problemas futuros
            if raw_code != code:
                logger.warning(
                    f"Código limpiado: '{raw_code}' -> '{code}' (len: {len(raw_code)} -> {len(code)})"
                )

            form = AlumnoForm()

            # Check if the code already exists (usando el código limpio)
            if Alumno.objects.filter(code=code).exists():
                user = Alumno.objects.get(code=code)
                user.count += 1
                user.save()
                logger.info(
                    f"Caja agregada a usuario existente: {code} (total: {user.count})"
                )
                result = f"Caja agregada correctamente a persona {code}"
                return HttpResponse(
                    template.render({"form": form, "result": result}, request)
                )

            # Create the Alumno con código limpio
            user = Alumno.objects.create(code=code)
            logger.info(f"Nuevo usuario creado: {code}")
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
    last = Alumno.objects.all().order_by("updated_at").last()

    # Verificar que los objetos existen antes de acceder a sus atributos
    if first and last:
        first_date = first.created_at.astimezone()
        last_date = last.updated_at.astimezone()
        writer.writerow(["Reporte de cajas", f"Desde {first_date} hasta {last_date}"])
    else:
        writer.writerow(["Reporte de cajas", "Sin datos de fechas disponibles"])

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


# Función administrativa para detectar y fusionar códigos duplicados
def fix_duplicate_codes(request: HttpRequest):
    """
    Función administrativa para detectar códigos que son esencialmente iguales
    pero que se guardaron como diferentes debido a espacios o caracteres unicode.
    """
    if request.method == "POST" and "confirm_fix" in request.POST:
        duplicates_fixed = 0
        codes_processed = set()

        for alumno in Alumno.objects.all():
            if alumno.code in codes_processed:
                continue

            cleaned_code = clean_barcode(alumno.code)

            # Si el código cambió después de limpiarlo, buscar duplicados
            if cleaned_code != alumno.code:
                # Buscar todos los códigos que se limpian al mismo valor
                similar_alumnos = []
                for other_alumno in Alumno.objects.all():
                    if clean_barcode(other_alumno.code) == cleaned_code:
                        similar_alumnos.append(other_alumno)
                        codes_processed.add(other_alumno.code)

                if len(similar_alumnos) > 1:
                    # Fusionar todos en el primer registro (con código limpio)
                    main_alumno = similar_alumnos[0]
                    main_alumno.code = cleaned_code
                    total_count = sum(a.count for a in similar_alumnos)
                    main_alumno.count = total_count
                    main_alumno.save()

                    # Eliminar los duplicados
                    for duplicate in similar_alumnos[1:]:
                        duplicate.delete()

                    duplicates_fixed += 1
                    logger.info(
                        f"Fusionados {len(similar_alumnos)} registros para código: {cleaned_code}"
                    )
            else:
                codes_processed.add(alumno.code)

        template = loader.get_template("index.html")
        result = f"Se fusionaron {duplicates_fixed} grupos de códigos duplicados"
        return HttpResponse(
            template.render({"form": AlumnoForm(), "result": result}, request)
        )

    # Mostrar previsualización de códigos que serían fusionados
    potential_duplicates = []
    codes_seen = {}

    for alumno in Alumno.objects.all():
        cleaned_code = clean_barcode(alumno.code)
        if cleaned_code in codes_seen:
            codes_seen[cleaned_code].append(alumno)
        else:
            codes_seen[cleaned_code] = [alumno]

    for cleaned_code, alumnos in codes_seen.items():
        if len(alumnos) > 1:
            total_count = sum(a.count for a in alumnos)
            original_codes = [a.code for a in alumnos]
            potential_duplicates.append(
                {
                    "cleaned_code": cleaned_code,
                    "original_codes": original_codes,
                    "total_count": total_count,
                    "count": len(alumnos),
                }
            )

    template = loader.get_template("confirm.html")
    context = {"potential_duplicates": potential_duplicates, "action": "fix_duplicates"}
    return HttpResponse(template.render(context, request))
