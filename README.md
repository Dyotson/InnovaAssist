# InnovaAssist

## Description

InnovaAssist es una simple WebApp para tomar asistencia en eventos. La idea es que los ayudantes puedan escanear el codigo de barra de la TUC del asistente para marcar su presencia en el evento.

## Instalación

Para instalar InnovaAssist, primero debes clonar el repositorio:

```bash
git clone https://github.com/Dyotson/InnovaAssist
```

Luego, para instalar y correr InnovaAssist debes instalar [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer) junto a [Python 3.12](https://www.python.org/downloads/). Una vez instalado, debes correr el siguiente comando en la carpeta raíz del proyecto:

```bash
poetry install
```

Luego, para correr la aplicación, debes correr el siguiente comando:

```bash
poetry run python manage.py runserver
```

## Licencia

InnovaAssist es un proyecto open-source bajo la licencia MIT. Para más información, revisa el archivo LICENSE.
