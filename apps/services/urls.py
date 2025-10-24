from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path("categories/", views.CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", views.CategoryDetailUpdateView.as_view(), name="category-detail-update"),
    path("categories/<int:pk>/servicemen/", views.CategoryServicemenListView.as_view(), name="category-servicemen"),
    
    # Service Requests
    path("service-requests/", views.ServiceRequestListCreateView.as_view(), name="service-request-list-create"),
    path("service-requests/<int:pk>/", views.ServiceRequestDetailView.as_view(), name="service-request-detail"),
    path("service-requests/<int:pk>/assign/", views.ServiceRequestAssignView.as_view(), name="service-request-assign"),
    
    # Serviceman Job History
    path("serviceman/job-history/", views.ServicemanJobHistoryView.as_view(), name="serviceman-job-history"),
]