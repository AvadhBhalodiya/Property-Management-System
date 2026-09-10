from django.urls import path

from apps.contracts.views import ContractListCreateView

app_name = "contracts"

urlpatterns = [
    path("contracts", ContractListCreateView.as_view(), name="contract-list"),
]
