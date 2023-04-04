#!/bin/bash


if [[ "$1" == "celery" ]]; then
  cd src/
  celery -A innotter worker -l info
elif [[ "$1" == "web" ]]; then
  cd src/
  python manage.py runserver 0.0.0.0:8000
elif [[ "$1" == "test" ]]; then
  python src/manage.py runserver 0.0.0.0:8000 & pytest src/tests/
else
  echo "Unknown argument. Usage: ./entrypoint.sh celery|web|pytest"
fi
