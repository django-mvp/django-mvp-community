"""The weekly digest, which django-generic-notifications leaves to the project."""

from django.utils.translation import gettext_lazy as _
from generic_notifications.frequencies import BaseFrequency, register


@register
class WeeklyFrequency(BaseFrequency):
    """Notifications gathered into one email a week."""

    key = "weekly"
    name = _("Weekly digest")
    is_realtime = False
    description = _("Bundle notifications into a weekly email")
