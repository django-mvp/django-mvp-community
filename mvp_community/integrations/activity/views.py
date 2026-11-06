"""The activity extra's views, over django-activity-stream's own queries."""

from actstream.models import Follow
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from mvp.views import MVPListView


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
