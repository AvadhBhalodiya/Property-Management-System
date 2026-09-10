from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from apps.properties.models import Property, Unit
from apps.properties.serializers import (
    PropertyDetailSerializer,
    PropertySerializer,
    UnitCreateSerializer,
    UnitSerializer,
)


class PropertyListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    success_messages = {
        "GET": "Properties fetched successfully",
        "POST": "Property created successfully",
    }

    def get_queryset(self):
        return Property.objects.annotate(unit_count=Count("units"))


class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.prefetch_related("units")
    serializer_class = PropertyDetailSerializer
    lookup_url_kwarg = "property_id"
    success_messages = {"GET": "Property fetched successfully"}


class UnitCreateView(generics.CreateAPIView):
    serializer_class = UnitCreateSerializer
    success_messages = {"POST": "Unit created successfully"}

    def perform_create(self, serializer):
        parent = get_object_or_404(Property, pk=self.kwargs["property_id"])
        serializer.save(property=parent)


class UnitListView(generics.ListAPIView):
    serializer_class = UnitSerializer
    success_messages = {"GET": "Units fetched successfully"}

    def get_queryset(self):
        queryset = Unit.objects.select_related("property")
        status = self.request.query_params.get("status")

        if status:
            if status not in Unit.Status.values:
                raise ValidationError({"status": "Invalid status."})
            queryset = queryset.filter(status=status)

        return queryset
