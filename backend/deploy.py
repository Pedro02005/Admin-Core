"""Initialize the hosted database after applying migrations."""

import os
from pathlib import Path

import django
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    if os.getenv("LOAD_DEMO_DATA") == "1":
        sql = Path(__file__).with_name("datos_demo.sql").read_text(encoding="utf-8")
        with connection.cursor() as cursor:
            cursor.execute(sql)

    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    if username and not get_user_model().objects.filter(username=username).exists():
        call_command("createsuperuser", interactive=False)


if __name__ == "__main__":
    main()
