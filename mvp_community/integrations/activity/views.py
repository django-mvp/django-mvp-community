"""The activity extra's views, over django-activity-stream's own queries."""

from actstream.models import Action, Follow
from actstream.registry import registry
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import View
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


class FollowControlView(LoginRequiredMixin, View):
    """The follow control of one object on its own, for htmx to swap in after a click."""

    http_method_names = ["get", "head", "options"]
    template_name = "mvp_community/activity/follow_control.html"

    def get_object(self, content_type_id, object_id):
        """Return the object the control belongs to.

        Args:
            content_type_id: The primary key of the object's content type.
            object_id: The object's primary key, as it appears in the address.

        Returns:
            The object, when its model is registered with django-activity-stream.

        Raises:
            Http404: When the type, the model's registration or the object is missing.
        """
        content_type = ContentType.objects.filter(pk=content_type_id).first()
        model = content_type.model_class() if content_type else None
        if model is None or model not in registry:
            raise Http404("No such followable type.")
        try:
            return model._default_manager.get(pk=object_id)
        except (ObjectDoesNotExist, ValueError, TypeError) as error:
            raise Http404("No such object.") from error

    def get(self, request, content_type_id, object_id):
        """Draw the follow control.

        Args:
            request: The request, whose ``next`` parameter is the page the control sits on.
            content_type_id: The primary key of the object's content type.
            object_id: The object's primary key.

        Returns:
            The control, without the page around it.
        """
        page = request.GET.get("next", "")
        if not url_has_allowed_host_and_scheme(
            page, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            page = "/"
        return render(
            request,
            self.template_name,
            {"object": self.get_object(content_type_id, object_id), "next": page},
        )
