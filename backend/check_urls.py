import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver
from rest_framework.routers import DefaultRouter
from dashboard.views import DashboardViewSet

# Check what the router generates
router = DefaultRouter()
router.register(r'', DashboardViewSet, basename='dashboard')

print("Router URLs:")
for pattern in router.urls:
    print(f"  {pattern.pattern}")

print("\nAll registered URLs:")
resolver = get_resolver()
for pattern in resolver.url_patterns:
    print(f"  {pattern}")
