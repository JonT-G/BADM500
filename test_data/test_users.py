"""
Creates test users. Wipes existing users first.

Usage: python test_data/test_users.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badm500.settings')
django.setup()

from django.contrib.auth.models import User

User.objects.all().delete()
print('  Wiped all users.')

User.objects.create_superuser(username='admin',   password='admin123')
User.objects.create_user(username='alice',        password='alice123')
User.objects.create_user(username='bob',          password='bob123')
User.objects.create_user(username='charlie',      password='charlie123')

print('  Created: admin (superuser), alice, bob, charlie.')
print('  Passwords: username + "123"  e.g. alice / alice123')
