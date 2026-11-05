"""Management command that gives the demo site activity and follows in every state."""

from datetime import timedelta

from actstream.actions import follow
from actstream.models import Action, Follow
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

PEOPLE = [
    ("anna@example.com", "Anna", "Weber"),
    ("ben@example.com", "Ben", "Okafor"),
    ("chloe@example.com", "Chloé", "Martin"),
    ("dmitri@example.com", "Dmitri", "Volkov"),
    ("esra@example.com", "Esra", "Yılmaz"),
    # A name long enough to wrap, so the rows can be judged with one.
    ("max@example.com", "Maximiliane Alexandra", "von Hohenstein-Liebenfels"),
]
# Enough extra people that staff.user follows more than one page holds.
CROWD = [(f"learner{n}@example.com", "Learner", f"{n:02d}") for n in range(1, 31)]
GROUPS = ["A1 Tenses", "Reading club", "Pronunciation clinic", "B2 Business German"]


class Command(BaseCommand):
    """Create people, groups, activity and follows, replacing any made before."""

    help = "Create the demo activity and follows."

    def handle(self, *args, **options):
        """Refuse unless DEBUG is on, then rebuild the demo activity."""
        if not settings.DEBUG:
            raise CommandError("seed_activity only runs with DEBUG on.")
        user_model = get_user_model()
        people = {}
        for email, first, last in PEOPLE + CROWD:
            person, _ = user_model.objects.update_or_create(
                **{user_model.USERNAME_FIELD: email},
                defaults={"email": email, "first_name": first, "last_name": last},
            )
            people[email] = person
        groups = {name: Group.objects.get_or_create(name=name)[0] for name in GROUPS}
        anna, ben, chloe, dmitri, esra, maxi = (people[p[0]] for p in PEOPLE)
        a1, club, clinic, b2 = (groups[g] for g in GROUPS)

        Action.objects.all().delete()
        Follow.objects.all().delete()
        now = timezone.now()
        # (minutes ago, actor, verb, action object, target, public, description)
        samples = [
            (4, anna, "finished", None, a1, True, ""),
            (25, ben, "joined", None, club, True, ""),
            (70, chloe, "posted in", None, club, True,
             "“Has anyone read Der Vorleser? I'd like to start it next week.”"),
            (180, dmitri, "finished", None, clinic, True, ""),
            (300, esra, "started", None, b2, True, ""),
            (400, maxi, "joined", None, a1, True, ""),
            (600, anna, "invited", ben, club, True, ""),
            (900, ben, "finished", None, a1, True, ""),
            (1500, anna, "joined", None, b2, False, ""),  # not public: in no feed
        ]
        # Older activity, so the feeds run past one page.
        for n in range(1, 40):
            actor = [anna, ben, chloe][n % 3]
            group = [a1, club, clinic, b2][n % 4]
            samples.append((2000 + n * 600, actor, ["finished", "joined", "posted in"][n % 3],
                            None, group, True, ""))
        for minutes, actor, verb, obj, target, public, description in samples:
            action = Action.objects.create(
                actor=actor, verb=verb, action_object=obj, target=target,
                public=public, description=description,
            )
            Action.objects.filter(pk=action.pk).update(timestamp=now - timedelta(minutes=minutes))

        regular = user_model.objects.get(email="regular.user@example.com")
        staff = user_model.objects.get(email="staff.user@example.com")
        for thing in (anna, ben, club):
            follow(regular, thing, actor_only=False, send_action=False)
        for thing in (anna, regular):
            follow(chloe, thing, actor_only=False, send_action=False)
        follow(ben, club, actor_only=False, send_action=False)
        for thing in list(people.values()) + list(groups.values()):
            follow(staff, thing, actor_only=False, send_action=False)
        # super.user follows nothing, so the empty feed and following page can be seen.
        self.stdout.write(self.style.SUCCESS(
            "regular.user follows Anna, Ben and the Reading club. staff.user follows "
            "everyone. super.user follows nothing."
        ))
