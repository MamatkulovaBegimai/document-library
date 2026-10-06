#!/usr/bin/env bash
# Render'дин "Build Command" катары колдонулат.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

python manage.py shell <<'EOF'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("ADMIN_USERNAME")
email = os.environ.get("ADMIN_EMAIL", "")
password = os.environ.get("ADMIN_PASSWORD")

if username and password:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email}
    )

    if created:
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print("Superuser created")
    else:
        print("Superuser already exists")
else:
    print("ADMIN_USERNAME or ADMIN_PASSWORD is not set")
EOF
