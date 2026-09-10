from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel
from apps.members.models import Member
from apps.properties.models import Unit


class ContractQuerySet(models.QuerySet):
    def active(self, on_date=None):
        on_date = on_date or timezone.localdate()
        return self.filter(start_date__lte=on_date, end_date__gte=on_date)

    def with_related(self):
        return self.select_related("member", "unit", "unit__property")


class Contract(TimeStampedModel):
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="contracts")
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="contracts")
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="contracts",
    )

    objects = ContractQuerySet.as_manager()

    class Meta:
        ordering = ["-start_date", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gt=models.F("start_date")),
                name="contract_end_date_after_start_date",
            )
        ]
        indexes = [models.Index(fields=["unit", "start_date", "end_date"])]

    def __str__(self):
        return f"{self.unit} - {self.member}"
