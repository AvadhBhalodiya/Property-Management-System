from rest_framework import serializers

from apps.properties.models import Property, Unit
from apps.properties.services import create_property, create_unit


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "property", "unit_number", "monthly_rent", "status", "created_at"]


class UnitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["unit_number", "monthly_rent"]

    def create(self, validated_data):
        return create_unit(**validated_data)

    def to_representation(self, instance):
        return UnitSerializer(instance).data


class PropertySerializer(serializers.ModelSerializer):
    unit_count = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = ["id", "name", "address", "unit_count", "created_at"]

    def get_unit_count(self, obj):
        if hasattr(obj, "unit_count"):
            return obj.unit_count

        return obj.units.count()

    def create(self, validated_data):
        return create_property(created_by=self.context["request"].user, **validated_data)


class PropertyDetailSerializer(serializers.ModelSerializer):
    units = UnitSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = ["id", "name", "address", "units", "created_at"]
