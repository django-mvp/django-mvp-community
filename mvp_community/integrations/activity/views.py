"""The feed page and the following page, over django-activity-stream's queries."""

from actstream.models import Action, Follow
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from mvp.views import MVPListView


class FeedView(LoginRequiredMixin, MVPListView):
    """The public activity of what the signed-in person follows, newest first."""

    model = Action
    template_name = "mvp_community/activity/feed.html"
    paginate_by = 20
    page_title = _("Feed")
    page_lead = _("What the people and things you follow have been doing.")
    breadcrumbs = [{"text": _("Feed")}]

    def get_queryset(self):
        """Return django-activity-stream's stream for the signed-in person."""
        return Action.objects.user(self.request.user)


class FollowingView(LoginRequiredMixin, MVPListView):
    """Everything the signed-in person follows."""

    model = Follow
    template_name = "mvp_community/activity/following.html"
    paginate_by = 20
    page_title = _("Following")
    page_lead = _("The people and things whose activity reaches your feed.")
    breadcrumbs = [{"text": _("Account Center")}, {"text": _("Following")}]

    def get_queryset(self):
        """Return the signed-in person's follows, newest first."""
        return (
            Follow.objects.filter(user=self.request.user)
            .select_related("content_type")
            .order_by("-started")
        )
