from django.urls import path
from . import views
from . import workflow_views

urlpatterns = [
    # Categories
    path("categories/", views.CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", views.CategoryDetailUpdateView.as_view(), name="category-detail-update"),
    path("categories/<int:pk>/servicemen/", views.CategoryServicemenListView.as_view(), name="category-servicemen"),
    
    # Service Requests
    path("service-requests/", views.ServiceRequestListCreateView.as_view(), name="service-request-list-create"),
    path("service-requests/<int:pk>/", views.ServiceRequestDetailView.as_view(), name="service-request-detail"),
    path("service-requests/<int:pk>/assign/", views.ServiceRequestAssignView.as_view(), name="service-request-assign"),
    
    # Professional Workflow Endpoints
    path("service-requests/<int:pk>/submit-estimate/", workflow_views.ServicemanSubmitEstimateView.as_view(), name="serviceman-submit-estimate"),
    path("service-requests/<int:pk>/finalize-price/", workflow_views.AdminFinalizePriceView.as_view(), name="admin-finalize-price"),
    path("service-requests/<int:pk>/authorize-work/", workflow_views.AdminAuthorizeWorkView.as_view(), name="admin-authorize-work"),
    path("service-requests/<int:pk>/complete-job/", workflow_views.ServicemanCompleteJobView.as_view(), name="serviceman-complete-job"),
    path("service-requests/<int:pk>/confirm-completion/", workflow_views.AdminConfirmCompletionView.as_view(), name="admin-confirm-completion"),
    path("service-requests/<int:pk>/submit-review/", workflow_views.ClientSubmitReviewView.as_view(), name="client-submit-review"),
    
    # Serviceman Job History
    path("serviceman/job-history/", views.ServicemanJobHistoryView.as_view(), name="serviceman-job-history"),
]