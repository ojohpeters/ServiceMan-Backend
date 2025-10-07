from django.urls import path
from . import views

urlpatterns = [
    path("", views.NegotiationListView.as_view(), name="negotiation-list"),
    path("create/", views.NegotiationCreateView.as_view(), name="negotiation-create"),
    path("<int:pk>/accept/", views.NegotiationAcceptView.as_view(), name="negotiation-accept"),
    path("<int:pk>/counter/", views.NegotiationCounterView.as_view(), name="negotiation-counter"),
]