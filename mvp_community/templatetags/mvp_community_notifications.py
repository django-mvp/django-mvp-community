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


@register.simple_tag
def notification_unsubscribe_url(recipient, type_keys):
    """Give the address that turns these notification types' email off.

    The unsubscribe module is imported inside the tag for the reason
    ``notifications_unread_count`` imports its library there.

    Args:
        recipient: The person the email is sent to.
        type_keys: A notification type key, or several.

    Returns:
        An absolute address, or an empty string when every type is one the
        project always sends by email.
    """
    from mvp_community.integrations.notifications.unsubscribe import UnsubscribeLink

    if isinstance(type_keys, str):
        type_keys = [type_keys]
    link = UnsubscribeLink.for_email(recipient, type_keys)
    return link.url() if link else ""


@register.simple_tag
def notification_type_name(key):
    """Give a notification type's name from its key, or the key when none is registered.

    Args:
        key: The notification type's key.

    Returns:
        The type's name.
    """
    from generic_notifications.registry import registry

    try:
        return registry.get_type(key).name
    except KeyError:
        return key
