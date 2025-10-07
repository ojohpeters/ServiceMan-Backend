import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from .models import Category

@pytest.mark.django_db
def test_category_create_and_list(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    url = reverse("category-create")
    data = {"name": "TestCat", "description": "desc"}
    response = client.post(url, data)
    assert response.status_code == 201
    url = reverse("category-list")
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_service_request_flow(client_user, category):
    client = APIClient()
    client.force_authenticate(user=client_user)
    url = reverse("service-request-create")
    data = {
        "category_id": category.id,
        "booking_date": "2025-10-05",
        "is_emergency": False,
        "client_address": "Test addr",
        "service_description": "Fix it",
    }
    response = client.post(url, data)
    assert response.status_code == 201