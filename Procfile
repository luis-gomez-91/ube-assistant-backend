web: cd assistant && python manage.py migrate --noinput && gunicorn assistant.wsgi:application --bind 0.0.0.0:$PORT
