#!/bin/bash
docker-compose run --rm app sh -c "python manage.py makemigrations core"
