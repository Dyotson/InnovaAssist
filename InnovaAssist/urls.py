"""
URL configuration for InnovaAssist project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from main.views import index, export_alumnos, delete_alumnos, fix_duplicate_codes

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("export_alumnos/", export_alumnos, name="export_alumnos"),
    path("delete_alumnos/", delete_alumnos, name="delete_alumnos"),
    path("fix_duplicates/", fix_duplicate_codes, name="fix_duplicates"),
]
