from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("categories/<int:pk>/servicemen/", views.CategoryServicemenListView.as_view(), name="category-servicemen"),
    path("categories/", views.CategoryCreateView.as_view(), name="category-create"),
    path("categories/<int:pk>/", views.CategoryUpdateView.as_view(), name="category-update"),
    path("service-requests/", views.ServiceRequestListView.as_view(), name="service-request-list"),
    path("service-requests/<int:pk>/", views.ServiceRequestDetailView.as_view(), name="service-request-detail"),
    path("service-requests/", views.ServiceRequestCreateView.as_view(), name="service-request-create"),
]