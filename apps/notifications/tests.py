import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from .models import Notification

@pytest.mark.django_db
def test_notification_list(client_user):
    Notification.objects.create(
        user=client_user,
        notification_type="SERVICE_ASSIGNED",
        title="Test",
        message="Test msg",
    )
    client = APIClient()
    client.force_authenticate(user=client_user)
    url = reverse("notification-list")
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()[0]['title'] == "Test"