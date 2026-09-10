import calendar
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta

from apps.contracts.models import Contract


def calculate_total_value(*, monthly_rent, start_date, end_date):
    span = relativedelta(end_date + timedelta(days=1), start_date)
    months = span.years * 12 + span.months
    total = monthly_rent * months

    if span.days:
        remainder_start = start_date + relativedelta(months=months)
        days_in_month = calendar.monthrange(remainder_start.year, remainder_start.month)[1]
        total += monthly_rent * span.days / days_in_month

    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def create_contract(*, unit, member, start_date, end_date, monthly_rent, created_by):
    if monthly_rent is None:
        monthly_rent = unit.monthly_rent

    total_value = calculate_total_value(
        monthly_rent=monthly_rent,
        start_date=start_date,
        end_date=end_date,
    )

    return Contract.objects.create(
        unit=unit,
        member=member,
        start_date=start_date,
        end_date=end_date,
        monthly_rent=monthly_rent,
        total_value=total_value,
        created_by=created_by,
    )
