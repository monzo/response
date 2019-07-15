#! /bin/bash

pip install -e /response

wait_for_db()
{
    while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432};
    do sleep 1;
    done;
}

create_admin_user()
{
    cat << EOF | python3 manage.py shell
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
User = get_user_model()
try:
    User.objects.create_superuser('admin', '', 'admin')
except IntegrityError:
    pass
EOF
}

echo "[INFO] Waiting for DB"
wait_for_db

echo "[INFO] Migrating database"
cd /app
python3 manage.py migrate --noinput

echo "[INFO] Creating Admin User"
create_admin_user

echo "[INFO] Starting Response Dev Server"
python3 manage.py runserver 0.0.0.0:8000
