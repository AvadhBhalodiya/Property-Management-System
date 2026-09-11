from rest_framework import generics
from rest_framework.exceptions import ValidationError

from apps.contracts.models import Contract
from apps.contracts.serializers import ContractCreateSerializer, ContractSerializer

TRUE_VALUES = {"true", "1"}
FALSE_VALUES = {"false", "0"}


class ContractListCreateView(generics.ListCreateAPIView):
    success_messages = {
        "GET": "Contracts fetched successfully",
        "POST": "Contract created successfully",
    }

    def get_queryset(self):
        queryset = Contract.objects.with_related()
        active = self.request.query_params.get("active")

        if active is None:
            return queryset

        value = active.lower()

        if value in TRUE_VALUES:
            return queryset.active()

        if value in FALSE_VALUES:
            return queryset.inactive()

        raise ValidationError({"active": "Must be true or false."})

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ContractCreateSerializer
        return ContractSerializer
