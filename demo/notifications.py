"""The demo project's notification types, so every state of the pages can be seen."""

from generic_notifications.channels import EmailChannel
from generic_notifications.frequencies import RealtimeFrequency
from generic_notifications.types import NotificationType, register


@register
class ReplyReceived(NotificationType):
    """Someone replied to something the person wrote."""

    key = "reply_received"
    name = "Replies"
    description = "When someone replies to something you wrote"


@register
class NewFollower(NotificationType):
    """Someone started following the person."""

    key = "new_follower"
    name = "New followers"
    description = "When someone starts following you"


@register
class CourseUpdated(NotificationType):
    """A course the person takes changed."""

    key = "course_updated"
    name = "Course updates"
    description = "When a course you are taking gets new material"


@register
class SecurityNotice(NotificationType):
    """Something changed about the person's account. Always sent by email."""

    key = "security_notice"
    name = "Security notices"
    description = "Sign-ins from a new device and changes to your account"
    required_channels = [EmailChannel]
    default_frequency = RealtimeFrequency
