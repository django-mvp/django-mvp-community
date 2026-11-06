"""The activity extra's views, over django-activity-stream's own queries."""

from actstream.models import Action, Follow
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from mvp.views import MVPListView


class ActivityFeedView(MVPListView):
    """A feed of public activity, which a host project mounts where it likes.

    Set ``stream`` as a class attribute or as an ``as_view()`` argument:

    - ``"site"``: the public activity of the whole site.
    - ``"object"``: the public activity around the object ``get_stream_object``
      returns.

    ``verb``, when set, limits the feed to that kind of activity.
    """

    model = Action
    template_name = "mvp_community/activity/feed.html"
    paginate_by = 20
    page_title = _("Activity")
    stream = None
    verb = ""

    def get_stream_object(self):
        """Return the object an ``"object"`` feed is about.

        Returns:
            The person or object whose activity to list.

        Raises:
            ImproperlyConfigured: Always, until a subclass overrides it.
        """
        raise ImproperlyConfigured(
            f"{type(self).__name__} streams an object, so it needs get_stream_object() "
            "to return one."
        )

    def get_queryset(self):
        """Return django-activity-stream's stream, newest first.

        Returns:
            The public activity the view's ``stream`` and ``verb`` select.

        Raises:
            ImproperlyConfigured: When ``stream`` is not one of the three.
        """
        arguments = {"verb": self.verb} if self.verb else {}
        if self.stream == "site":
            # Unlike the other streams, public() does not fetch each action's
            # actor, target and action object in bulk.
            return Action.objects.public(**arguments).fetch_generic_relations()
        if self.stream == "object":
            return Action.objects.any(self.get_stream_object(), **arguments)
        raise ImproperlyConfigured(
            f"{type(self).__name__}.stream must be 'site' or 'object', not {self.stream!r}."
        )


class FollowingView(LoginRequiredMixin, MVPListView):
    """Everything the signed-in person follows, newest first."""

    model = Follow
    template_name = "mvp_community/activity/following.html"
    paginate_by = 20
    page_title = _("Following")
    page_lead = _("The people and things whose activity reaches your feed.")
    breadcrumbs = [{"text": _("Account Center")}, {"text": _("Following")}]

    def get_queryset(self):
        """Return the signed-in person's follows, newest first.

        Returns:
            django-activity-stream's follows of the signed-in person.
        """
        return Follow.objects.following_qs(self.request.user).order_by("-started")
