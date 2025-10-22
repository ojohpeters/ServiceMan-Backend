from django.urls import path
from .views import InitializeBookingFeeView, InitializePaymentView, PaystackWebhookView, PaymentVerifyView

urlpatterns = [
    path("initialize-booking-fee/", InitializeBookingFeeView.as_view(), name="initialize-booking-fee"),
    path("initialize/", InitializePaymentView.as_view(), name="initialize-payment"),
    path("webhook/", PaystackWebhookView.as_view(), name="paystack-webhook"),
    path("verify/", PaymentVerifyView.as_view(), name="payment-verify"),
]