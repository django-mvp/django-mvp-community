"""What the preferences page needs to draw the push card."""

from django.urls import reverse_lazy
from push_notifications.models import WebPushDevice


def card_context(request):
    """Build what the push card renders for the signed-in person.

    Args:
        request: The preferences page's request.

    Returns:
        A dict with the person's active ``subscriptions``, newest first, and
        the ``worker_url`` and ``subscribe_url`` the card's script uses. The
        URLs resolve when they are rendered, so a project that has not
        included the push routes fails on the card, not on every page.
    """
    return {
        "subscriptions": WebPushDevice.objects.filter(
            user=request.user, active=True
        ).order_by("-date_created", "-pk"),
        "worker_url": reverse_lazy("mvp_community_push:worker"),
        "subscribe_url": reverse_lazy("mvp_community_push:subscribe"),
    }
