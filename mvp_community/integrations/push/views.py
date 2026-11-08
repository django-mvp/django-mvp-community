"""The views that turn push on for a browser."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView
from push_notifications.models import WebPushDevice

from .channels import PushChannel
from .subscriptions import SESSION_KEY, Browser, is_push_endpoint

NAME_LENGTH = 255
P256DH_LENGTH = 88
AUTH_LENGTH = 24


@method_decorator(
    [login_not_required, cache_control(no_cache=True)],
    name="dispatch",
)
class WorkerView(TemplateView):
    """Serve the service worker that shows a push and opens it on a click.

    A browser fetches it signed out too, and checks it for a change on every
    visit, so it is never kept without revalidating.
    """

    template_name = "mvp_community/push/worker.js"
    content_type = "text/javascript"


class SubscribeView(LoginRequiredMixin, View):
    """Store the push subscription a browser made and send it a test push."""

    http_method_names = ["post", "options"]
    raise_exception = True

    def read(self, request):
        """Read and check the subscription a browser posted.

        Args:
            request: The POST request carrying the browser's JSON.

        Returns:
            A tuple of the endpoint, the ``p256dh`` key and the ``auth``
            secret, or None when anything is missing, too long or not accepted.
        """
        try:
            data = json.loads(request.body)
        except ValueError:
            return None
        if not isinstance(data, dict) or not isinstance(data.get("keys"), dict):
            return None
        endpoint = data.get("endpoint")
        p256dh = data["keys"].get("p256dh")
        auth = data["keys"].get("auth")
        if not all(
            isinstance(value, str) and value for value in (endpoint, p256dh, auth)
        ):
            return None
        if len(p256dh) > P256DH_LENGTH or len(auth) > AUTH_LENGTH:
            return None
        if not is_push_endpoint(endpoint):
            return None
        return endpoint, p256dh, auth

    def post(self, request):
        """Store the subscription, remember it for the card and send a test.

        One row is kept for each person and endpoint, so turning push on again
        in the same browser updates it.

        Args:
            request: The POST request carrying the browser's JSON.

        Returns:
            A 204, or a 400 with nothing stored when the JSON is not accepted.
        """
        fields = self.read(request)
        if fields is None:
            return HttpResponseBadRequest()
        endpoint, p256dh, auth = fields
        subscription = WebPushDevice.objects.update_or_create(
            user=request.user,
            registration_id=endpoint,
            defaults={
                "p256dh": p256dh,
                "auth": auth,
                "active": True,
                "name": request.headers.get("User-Agent", "")[:NAME_LENGTH],
            },
        )[0]
        request.session[SESSION_KEY] = True
        PushChannel().send_test(subscription)
        return HttpResponse(status=204)


class StopView(LoginRequiredMixin, View):
    """Stop push to one of the signed-in person's browsers."""

    http_method_names = ["post", "options"]
    raise_exception = True

    def post(self, request, pk):
        """Delete the subscription and go back to the preferences page.

        Another person's subscription is a 404 and changes nothing. The
        browser's own push subscription is left alone, because a browser shared
        by two people has one endpoint for both.

        Args:
            request: The POST request from the row's Stop button.
            pk: The id of the subscription to stop.

        Returns:
            A redirect to the notification preferences page.
        """
        subscription = get_object_or_404(WebPushDevice, pk=pk, user=request.user)
        label = Browser.from_user_agent(subscription.name).label
        subscription.delete()
        messages.success(
            request, _("Push to %(browser)s is stopped.") % {"browser": label}
        )
        return redirect(reverse("mvp_community_notifications:preferences"))
