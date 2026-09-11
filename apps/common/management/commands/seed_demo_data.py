from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.contracts.services import create_contract
from apps.members.models import Member
from apps.properties.models import Property, Unit
from apps.users.models import User

DEMO_EMAIL = "staff@example.com"
DEMO_PASSWORD = "Staff@123"

PROPERTIES = [
    ("Marine Drive Residency", "12 Marine Drive, Mumbai 400020"),
    ("Koramangala Heights", "5th Block, Koramangala, Bengaluru 560095"),
]

UNITS = [
    ("Marine Drive Residency", "A-101", "32000.00"),
    ("Marine Drive Residency", "A-102", "28500.50"),
    ("Koramangala Heights", "B-201", "45000.00"),
    ("Koramangala Heights", "B-202", "41000.00"),
]

MEMBERS = [
    ("Rohit Sharma", "rohit.sharma@example.com"),
    ("Neha Patel", "neha.patel@example.com"),
]


class Command(BaseCommand):
    help = "Create a demo staff user with sample properties, units, members and a running contract"

    @transaction.atomic
    def handle(self, *args, **options):
        staff = User.objects.filter(email=DEMO_EMAIL).first()
        if staff is None:
            staff = User.objects.create_user(
                email=DEMO_EMAIL,
                full_name="Demo Staff",
                password=DEMO_PASSWORD,
            )

        properties = {}
        for name, address in PROPERTIES:
            obj, _ = Property.objects.get_or_create(
                name=name,
                defaults={"address": address, "created_by": staff},
            )
            properties[name] = obj

        for property_name, unit_number, monthly_rent in UNITS:
            Unit.objects.get_or_create(
                property=properties[property_name],
                unit_number=unit_number,
                defaults={"monthly_rent": Decimal(monthly_rent)},
            )

        members = []
        for full_name, email in MEMBERS:
            obj, _ = Member.objects.get_or_create(email=email, defaults={"full_name": full_name})
            members.append(obj)

        demo_unit = Unit.objects.get(property=properties["Koramangala Heights"], unit_number="B-202")

        if not demo_unit.contracts.exists():
            today = timezone.localdate()
            create_contract(
                unit=demo_unit,
                member=members[0],
                start_date=today - timedelta(days=30),
                end_date=today + timedelta(days=334),
                monthly_rent=None,
                created_by=staff,
            )

        self.stdout.write(f"demo data ready, login with {DEMO_EMAIL} / {DEMO_PASSWORD}")
