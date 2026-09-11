import calendar
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.contracts.models import Contract
from apps.properties.models import Unit
from apps.properties.services import set_unit_status


def calculate_total_value(*, monthly_rent, start_date, end_date):
    span = relativedelta(end_date + timedelta(days=1), start_date)
    months = span.years * 12 + span.months
    total = monthly_rent * months

    if span.days:
        remainder_start = start_date + relativedelta(months=months)
        days_in_month = calendar.monthrange(remainder_start.year, remainder_start.month)[1]
        total += monthly_rent * span.days / days_in_month

    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def has_overlapping_contract(*, unit, start_date, end_date):
    return Contract.objects.filter(
        unit=unit,
        start_date__lte=end_date,
        end_date__gte=start_date,
    ).exists()


def refresh_unit_status(*, unit, on_date=None):
    is_occupied = Contract.objects.filter(unit=unit).active(on_date).exists()
    status = Unit.Status.OCCUPIED if is_occupied else Unit.Status.AVAILABLE
    set_unit_status(unit=unit, status=status)


@transaction.atomic
def create_contract(*, unit, member, start_date, end_date, monthly_rent, created_by):
    unit = Unit.objects.select_for_update().get(pk=unit.pk)

    if monthly_rent is None:
        monthly_rent = unit.monthly_rent

    if has_overlapping_contract(unit=unit, start_date=start_date, end_date=end_date):
        raise ValidationError({"unit": "This unit is already booked for the selected dates."})

    total_value = calculate_total_value(
        monthly_rent=monthly_rent,
        start_date=start_date,
        end_date=end_date,
    )

    contract = Contract.objects.create(
        unit=unit,
        member=member,
        start_date=start_date,
        end_date=end_date,
        monthly_rent=monthly_rent,
        total_value=total_value,
        created_by=created_by,
    )

    refresh_unit_status(unit=unit)

    return contract
