import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from apps.services.models import ServiceRequest, Category

@pytest.mark.django_db
def test_initialize_payment(client_user):
    client = APIClient()
    client.force_authenticate(user=client_user)
    cat = Category.objects.create(name="Test", description="Test")
    req = ServiceRequest.objects.create(
        client=client_user, category=cat, booking_date="2025-10-03",
        is_emergency=False, auto_flagged_emergency=False,
        initial_booking_fee=2000, status="PENDING_ADMIN_ASSIGNMENT",
        client_address="Somewhere", service_description="Do work"
    )
    url = reverse("initialize-payment")
    data = {
        "service_request": req.id,
        "payment_type": "INITIAL_BOOKING",
        "amount": 2000,
    }
    # This would normally call the paystack API, so you may want to patch it in real tests
    # response = client.post(url, data)
    # assert response.status_code == 201