"""The notifications extra, built on django-generic-notifications."""

from generic_notifications.registry import registry
from generic_notifications.types import SystemMessage

from . import frequencies  # noqa: F401  (registers the weekly digest)

# django-generic-notifications registers an English-only "System Message" type of
# its own. A host project declares the types it sends, so it is removed here.
registry.unregister_type(SystemMessage)
