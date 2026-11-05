"""The signed-in person's unread count, for the bell in the shell."""

from generic_notifications.utils import get_unread_count


def notifications(request):
    """Return the unread count on the site, or nothing for a signed-out visit."""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {}
    return {"notifications_unread": get_unread_count(user)}
