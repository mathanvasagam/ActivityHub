from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Set exactly two organization admins and keep all other users as normal users."

    def add_arguments(self, parser):
        parser.add_argument(
            "usernames",
            nargs=2,
            help="Exactly two existing usernames that should become admins.",
        )

    def handle(self, *args, **options):
        usernames = options["usernames"]
        User = get_user_model()

        missing = [username for username in usernames if not User.objects.filter(username=username).exists()]
        if missing:
            raise CommandError(f"These usernames do not exist: {', '.join(missing)}")

        # Reset all users to standard user role first.
        User.objects.all().update(is_staff=False, is_superuser=False)

        # Promote the two selected users to full admins.
        updated = User.objects.filter(username__in=usernames).update(is_staff=True, is_superuser=True)

        self.stdout.write(self.style.SUCCESS(f"Set {updated} users as admins: {', '.join(usernames)}"))
