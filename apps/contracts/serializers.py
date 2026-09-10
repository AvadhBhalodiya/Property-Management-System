from rest_framework import serializers

from apps.contracts.models import Contract
from apps.contracts.services import create_contract
from apps.members.serializers import MemberSerializer
from apps.properties.serializers import UnitSerializer


class ContractSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(read_only=True)
    member = MemberSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = [
            "id",
            "unit",
            "member",
            "start_date",
            "end_date",
            "monthly_rent",
            "total_value",
            "created_at",
        ]


class ContractCreateSerializer(serializers.ModelSerializer):
    monthly_rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Contract
        fields = ["unit", "member", "start_date", "end_date", "monthly_rent"]

    def validate(self, attrs):
        if attrs["end_date"] <= attrs["start_date"]:
            raise serializers.ValidationError({"end_date": "End date must be after start date."})
        return attrs

    def create(self, validated_data):
        return create_contract(
            created_by=self.context["request"].user,
            monthly_rent=validated_data.pop("monthly_rent", None),
            **validated_data,
        )

    def to_representation(self, instance):
        return ContractSerializer(instance).data
