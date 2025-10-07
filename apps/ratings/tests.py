import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from apps.services.models import ServiceRequest, Category
from .models import Rating

@pytest.mark.django_db
def test_rating_creation_and_analytics(client_user, serviceman_user):
    cat = Category.objects.create(name="Test", description="desc")
    req = ServiceRequest.objects.create(
        client=client_user, category=cat, booking_date="2025-10-11",
        is_emergency=False, auto_flagged_emergency=False,
        initial_booking_fee=2000, status="COMPLETED",
        client_address="Addr", service_description="Desc",
        serviceman=serviceman_user
    )
    client = APIClient()
    client.force_authenticate(user=client_user)
    url = reverse("rating-create")
    data = {
        "service_request": req.id,
        "rating": 5,
        "review": "Excellent work"
    }
    response = client.post(url, data)
    assert response.status_code == 201 or response.status_code == 200

    # Analytics
    client.force_authenticate(user=User.objects.create(username="admin", user_type="ADMIN", is_superuser=True))
    url = reverse("analytics-servicemen")
    response = client.get(url)
    assert response.status_code == 200