import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_user_registration(client):
    url = reverse("users:register")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Testpass123!",
        "user_type": "CLIENT"
    }
    response = client.post(url, data)
    assert response.status_code == 201
    assert User.objects.filter(email="test@example.com").exists()

@pytest.mark.django_db
def test_resend_verification_email(client):
    # Create an unverified user
    user = User.objects.create_user(
        username="testuser2",
        email="test2@example.com",
        password="Testpass123!",
        user_type="CLIENT"
    )
    user.is_email_verified = False
    user.save()
    
    # Test resend verification email
    url = reverse("users:resend-verification-email")
    data = {"email": "test2@example.com"}
    response = client.post(url, data)
    assert response.status_code == 200
    assert "Verification email sent" in response.data["detail"]

@pytest.mark.django_db
def test_resend_verification_email_already_verified(client):
    # Create a verified user
    user = User.objects.create_user(
        username="testuser3",
        email="test3@example.com",
        password="Testpass123!",
        user_type="CLIENT"
    )
    user.is_email_verified = True
    user.save()
    
    # Test resend verification email for already verified user
    url = reverse("users:resend-verification-email")
    data = {"email": "test3@example.com"}
    response = client.post(url, data)
    assert response.status_code == 400
    assert "already verified" in response.data["detail"]

@pytest.mark.django_db
def test_resend_verification_email_nonexistent_user(client):
    # Test resend verification email for non-existent user
    url = reverse("users:resend-verification-email")
    data = {"email": "nonexistent@example.com"}
    response = client.post(url, data)
    assert response.status_code == 200
    assert "verification email has been sent" in response.data["detail"]