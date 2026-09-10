from django.urls import path

from apps.properties.views import (
    PropertyDetailView,
    PropertyListCreateView,
    UnitCreateView,
    UnitListView,
)

urlpatterns = [
    path("properties", PropertyListCreateView.as_view(), name="property-list"),
    path("properties/<int:property_id>", PropertyDetailView.as_view(), name="property-detail"),
    path("properties/<int:property_id>/units", UnitCreateView.as_view(), name="property-unit-create"),
    path("units", UnitListView.as_view(), name="unit-list"),
]
