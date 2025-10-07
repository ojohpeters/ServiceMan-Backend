import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from apps.services.models import Category, ServiceRequest

@pytest.mark.django_db
def test_negotiation_flow(client_user, admin_user):
    cat = Category.objects.create(name="Test", description="desc")
    req = ServiceRequest.objects.create(
        client=client_user, category=cat, booking_date="2025-10-05",
        is_emergency=False, auto_flagged_emergency=False,
        initial_booking_fee=2000, status="NEGOTIATING",
        client_address="Addr", service_description="Desc"
    )
    client = APIClient()
    client.force_authenticate(user=client_user)
    create_url = reverse("negotiation-create")
    data = {
        "service_request": req.id,
        "proposed_amount": 15000,
        "message": "Can you do 15k?"
    }
    response = client.post(create_url, data)
    assert response.status_code == 201 or response.status_code == 200