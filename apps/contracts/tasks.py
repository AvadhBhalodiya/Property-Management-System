from celery import shared_task

from apps.contracts import services


@shared_task
def sync_unit_statuses():
    return services.sync_unit_statuses()
