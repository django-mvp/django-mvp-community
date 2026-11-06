"""The one stream this package shapes beyond django-activity-stream's own."""

from actstream.models import Action
from django.contrib.contenttypes.models import ContentType


def followed_activity(user, **filters):
    """Return the public activity of what ``user`` follows, without their own actions.

    django-activity-stream's ``user`` stream also holds the person's own actions
    where they act on something they follow, and the "started following" each
    follow records. The feed of what a person follows leaves those out.

    Args:
        user: The signed-in person.
        **filters: Passed to the stream, such as ``verb``.

    Returns:
        The stream, newest first.
    """
    return Action.objects.user(user, **filters).exclude(
        actor_content_type=ContentType.objects.get_for_model(user),
        actor_object_id=str(user.pk),
    )
