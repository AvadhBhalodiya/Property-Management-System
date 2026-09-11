from rest_framework import generics

from apps.contracts.models import Contract
from apps.contracts.serializers import ContractCreateSerializer, ContractSerializer


class ContractListCreateView(generics.ListCreateAPIView):
    success_messages = {
        "GET": "Contracts fetched successfully",
        "POST": "Contract created successfully",
    }

    def get_queryset(self):
        queryset = Contract.objects.with_related()

        if self.request.query_params.get("active"):
            queryset = queryset.active()

        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ContractCreateSerializer
        return ContractSerializer
