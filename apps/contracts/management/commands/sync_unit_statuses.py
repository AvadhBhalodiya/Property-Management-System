from django.core.management.base import BaseCommand

from apps.contracts import services


class Command(BaseCommand):
    help = "Sync unit status with the contracts that are active today"

    def handle(self, *args, **options):
        result = services.sync_unit_statuses()
        self.stdout.write(f"occupied: {result['occupied']}, released: {result['released']}")
