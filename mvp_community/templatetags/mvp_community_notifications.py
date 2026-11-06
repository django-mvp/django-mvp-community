"""Template tags for the notifications extra."""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def notifications_unread_count(context):
    """Count the signed-in person's unread notifications on the site.

    django-generic-notifications is imported inside the tag, not at the top of
    the module, because Django only finds a tag library under this package's
    ``templatetags`` and a project installed without the extra still loads it.

    Args:
        context: The template context, which carries the request.

    Returns:
        The unread count, or None for a signed-out visitor or a context
        with no request.
    """
    request = context.get("request")
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return None

    from generic_notifications.utils import get_unread_count

    return get_unread_count(user)


UNSUBSCRIBE_SALT = "mvp_community.notifications.unsubscribe"


@register.simple_tag
def notification_unsubscribe_token(recipient, *type_keys):
    """Sign which person and which notification types an unsubscribe link turns off.

    Args:
        recipient: The person the email is sent to.
        *type_keys: The notification type keys, or lists of them.

    Returns:
        A signed token for the unsubscribe page's address.
    """
    from django.core import signing

    keys = []
    for item in type_keys:
        keys.extend([item] if isinstance(item, str) else list(item))
    return signing.dumps({"u": recipient.pk, "t": sorted(set(keys))}, salt=UNSUBSCRIBE_SALT)


@register.simple_tag
def notification_type_name(key):
    """Give a notification type's name from its key, or the key when none is registered.

    Args:
        key: The notification type's key.

    Returns:
        The type's name.
    """
    from generic_notifications.registry import registry

    for notification_type in registry.get_all_types():
        if notification_type.key == key:
            return notification_type.name
    return key
