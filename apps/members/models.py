from django.db import models

from apps.common.models import TimeStampedModel


class Member(TimeStampedModel):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name
