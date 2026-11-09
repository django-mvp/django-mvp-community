"""The system check that guards the settings push cannot work without."""

from django.core.checks import Error, register
from push_notifications.settings import PUSH_NOTIFICATIONS_SETTINGS

HINT = "See the push guide in the documentation for how to generate and set it."


@register()
def check_push_settings(app_configs, **kwargs):
    """Report each setting the push service needs that is empty.

    The library fills ``WP_PRIVATE_KEY`` and ``WP_CLAIMS`` with ``None`` when
    it loads, so this reads its settings dict and tests for an empty value
    rather than for a missing key.

    Args:
        app_configs: The app configs being checked, which this check ignores.
        **kwargs: The other arguments Django passes to a check.

    Returns:
        One error for each setting that is empty, naming it.
    """
    errors = []
    if not PUSH_NOTIFICATIONS_SETTINGS.get("WP_PRIVATE_KEY"):
        errors.append(
            Error(
                "PUSH_NOTIFICATIONS_SETTINGS has no WP_PRIVATE_KEY, so push "
                "cannot be sent or turned on.",
                hint=HINT,
                id="mvp_community.E002",
            )
        )
    claims = PUSH_NOTIFICATIONS_SETTINGS.get("WP_CLAIMS")
    if not claims or not claims.get("sub"):
        errors.append(
            Error(
                "PUSH_NOTIFICATIONS_SETTINGS has no WP_CLAIMS with a 'sub' "
                "contact, which push services require.",
                hint=HINT,
                id="mvp_community.E002",
            )
        )
    return errors
