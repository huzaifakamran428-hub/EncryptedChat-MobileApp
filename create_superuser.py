"""Creates (or promotes) the admin account. Runs from build.sh on every deploy.

Needs these environment variables on Render:
  DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
Optional: DJANGO_SUPERUSER_USERNAME (default: admin)
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatapp.settings")

try:
    django.setup()
except Exception as e:
    print(f"[superuser] django.setup() failed: {e}")
    sys.exit(0)

from django.contrib.auth import get_user_model

User = get_user_model()
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin").strip() or "admin"

if not email or not password:
    print("[superuser] Email or password not set - skipping")
    sys.exit(0)

try:
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        # Make sure the username is free
        base, n = username, 1
        while User.objects.filter(username=username).exists():
            n += 1
            username = f"{base}{n}"
        user = User(username=username, email=email)
        action = "Created"
    else:
        action = "Promoted existing"
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()
    print(f'[superuser] {action} superuser "{user.username}" ({email})')
except Exception as e:
    print(f"[superuser] ERROR: {e}")

sys.exit(0)
