from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from searcher.models import BlogPost, LinkedInPost, Project, ResearchPaper, UserProfile


class Command(BaseCommand):
    help = "Seed demo users and mock social content data for admin testing."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=10, help="Number of demo users to create.")
        parser.add_argument("--password", type=str, default="Demo@12345", help="Password for demo users.")
        parser.add_argument("--create-admin", action="store_true", help="Create a default demo admin account.")

    @transaction.atomic
    def handle(self, *args, **options):
        user_model = get_user_model()
        total_users = max(1, options["users"])
        password = options["password"]

        companies = [
            "Nova Labs",
            "Acme Systems",
            "Pioneer Cloud",
            "Orbit Health",
            "BrightForge",
        ]
        platforms = ["Medium", "Dev.to", "Hashnode", "Substack", "Personal Site"]
        publications = ["ArXiv", "IEEE", "ACM", "Nature", "Springer"]

        created_count = 0
        updated_count = 0

        now = timezone.now()
        today = timezone.localdate()

        for index in range(1, total_users + 1):
            username = f"demo_user_{index:02d}"
            email = f"{username}@activityhub.local"

            user, created = user_model.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                },
            )
            user.email = email
            user.set_password(password)
            user.save(update_fields=["email", "password"])

            if created:
                created_count += 1
            else:
                updated_count += 1

            profile, _ = UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": f"Demo Member {index}",
                    "role_title": f"Content Specialist {index}",
                    "linkedin_profile_url": f"https://www.linkedin.com/in/{username}",
                    "about": "Demo profile generated for admin filtering and export validation.",
                },
            )

            for post_index in range(1, 6):
                posted_at = now - timedelta(days=(index * 2 + post_index), hours=post_index)
                LinkedInPost.objects.update_or_create(
                    post_url=f"https://social.example.com/{username}/post-{post_index}",
                    defaults={
                        "user": user,
                        "profile": profile,
                        "post_title": f"Campaign update {post_index} for {username}",
                        "company_name": companies[(index + post_index) % len(companies)],
                        "posted_at": posted_at,
                        "notes": "Mock social post for export tests.",
                    },
                )

            for project_index in range(1, 3):
                start_date = today - timedelta(days=index * 10 + project_index * 15)
                Project.objects.update_or_create(
                    user=user,
                    name=f"Project {project_index} - {username}",
                    defaults={
                        "description": "Demo project timeline for dashboard stats.",
                        "start_date": start_date,
                        "end_date": start_date + timedelta(days=30),
                    },
                )

            for blog_index in range(1, 3):
                BlogPost.objects.update_or_create(
                    url=f"https://blog.example.com/{username}/entry-{blog_index}",
                    defaults={
                        "user": user,
                        "title": f"Blog insight {blog_index} by {username}",
                        "platform": platforms[(index + blog_index) % len(platforms)],
                        "published_on": today - timedelta(days=index * 3 + blog_index),
                        "summary": "Mock blog entry used for sample content coverage.",
                    },
                )

            for paper_index in range(1, 3):
                ResearchPaper.objects.update_or_create(
                    url=f"https://research.example.com/{username}/paper-{paper_index}",
                    defaults={
                        "user": user,
                        "title": f"Research note {paper_index} by {username}",
                        "publication": publications[(index + paper_index) % len(publications)],
                        "published_on": today - timedelta(days=index * 5 + paper_index),
                        "abstract": "Mock research record for admin reporting and exports.",
                    },
                )

        if options["create_admin"]:
            admin_user, _ = user_model.objects.get_or_create(
                username="admin_demo",
                defaults={"email": "admin_demo@activityhub.local", "is_staff": True, "is_superuser": True},
            )
            admin_user.email = "admin_demo@activityhub.local"
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password(password)
            admin_user.save(update_fields=["email", "is_staff", "is_superuser", "password"])
            self.stdout.write(self.style.SUCCESS("Admin user ready: admin_demo"))

        self.stdout.write(self.style.SUCCESS(f"Seed completed. Created users: {created_count}, updated users: {updated_count}"))
        self.stdout.write(self.style.SUCCESS(f"Demo user password: {password}"))
