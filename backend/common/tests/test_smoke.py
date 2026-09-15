import psycopg
from django.conf import settings


def test_settings_loaded():
    assert settings.AUTH_USER_MODEL == "accounts.User"


def test_database_connection():
    db = settings.DATABASES["default"]
    conn = psycopg.connect(
        host=db["HOST"],
        port=db["PORT"],
        dbname=db["NAME"],
        user=db["USER"],
        password=db["PASSWORD"],
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone() == (1,)
    finally:
        conn.close()
