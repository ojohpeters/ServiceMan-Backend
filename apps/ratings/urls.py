from django.urls import path
from .views import (
    RatingCreateView, RatingListView,
    RevenueAnalyticsView, TopServicemenAnalyticsView, TopCategoriesAnalyticsView,
)

urlpatterns = [
    path("", RatingListView.as_view(), name="rating-list"),
    path("create/", RatingCreateView.as_view(), name="rating-create"),
    path("analytics/revenue/", RevenueAnalyticsView.as_view(), name="analytics-revenue"),
    path("analytics/servicemen/", TopServicemenAnalyticsView.as_view(), name="analytics-servicemen"),
    path("analytics/categories/", TopCategoriesAnalyticsView.as_view(), name="analytics-categories"),
]