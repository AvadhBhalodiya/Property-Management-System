from rest_framework.exceptions import ValidationError

from apps.properties.models import Property, Unit


def create_property(*, name, address, created_by):
    return Property.objects.create(name=name, address=address, created_by=created_by)


def create_unit(*, property, unit_number, monthly_rent):
    if Unit.objects.filter(property=property, unit_number=unit_number).exists():
        raise ValidationError({"unit_number": "This unit number already exists for the property."})

    return Unit.objects.create(property=property, unit_number=unit_number, monthly_rent=monthly_rent)


def set_unit_status(*, unit, status):
    if unit.status == status:
        return unit

    unit.status = status
    unit.save(update_fields=["status", "updated_at"])
    return unit
