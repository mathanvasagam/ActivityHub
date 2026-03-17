from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import PostFilterForm
from .models import LinkedInPost, UserProfile


class DashboardFlowTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="member", password="secure-pass-123")

    def test_home_requires_login(self):
        response = self.client.get(reverse("searcher:home"))
        self.assertEqual(response.status_code, 302)

    def test_user_can_save_profile(self):
        self.client.login(username="member", password="secure-pass-123")
        payload = {
            "full_name": "Member User",
            "role_title": "Marketing",
            "linkedin_profile_url": "https://www.linkedin.com/in/member-user",
            "about": "Handles social media activity",
        }
        response = self.client.post(reverse("searcher:profile"), payload)
        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.full_name, "Member User")

    def test_user_can_add_post(self):
        self.client.login(username="member", password="secure-pass-123")
        UserProfile.objects.create(
            user=self.user,
            full_name="Member User",
            role_title="Marketing",
            linkedin_profile_url="https://www.linkedin.com/in/member-user",
        )
        payload = {
            "post_title": "Launch update",
            "company_name": "Forge Innovation and Ventures",
            "posted_at": "2026-03-15T10:15",
            "post_url": "https://www.linkedin.com/posts/member-launch-update",
            "notes": "Organic engagement campaign",
        }
        response = self.client.post(reverse("searcher:post-create"), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(LinkedInPost.objects.filter(user=self.user).count(), 1)


class OrganizationViewTests(TestCase):
    def setUp(self) -> None:
        self.staff = User.objects.create_user(username="admin1", password="secure-pass-123", is_staff=True)
        self.user = User.objects.create_user(username="member", password="secure-pass-123")

        profile = UserProfile.objects.create(
            user=self.user,
            full_name="Member User",
            role_title="Marketing",
            linkedin_profile_url="https://www.linkedin.com/in/member-user",
        )
        LinkedInPost.objects.create(
            user=self.user,
            profile=profile,
            post_title="Q1 Insights",
            company_name="Forge Innovation and Ventures",
            posted_at=timezone.now() - timedelta(days=2),
            post_url="https://www.linkedin.com/posts/member-q1-insights",
        )

    def test_non_staff_cannot_access_organization_page(self):
        self.client.login(username="member", password="secure-pass-123")
        response = self.client.get(reverse("searcher:organization"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_filter_organization_data(self):
        self.client.login(username="admin1", password="secure-pass-123")
        response = self.client.get(reverse("searcher:organization"), {"company_name": "forge"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Q1 Insights")

    def test_staff_can_export_csv(self):
        self.client.login(username="admin1", password="secure-pass-123")
        response = self.client.get(reverse("searcher:export-posts-csv"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])

    def test_staff_can_export_single_user_report_csv(self):
        self.client.login(username="admin1", password="secure-pass-123")
        response = self.client.get(reverse("searcher:export-user-posts-csv", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("member_posts_report.csv", response["Content-Disposition"])
        body = response.content.decode("utf-8")
        self.assertIn("report,single_user_posts", body)
        self.assertIn("Q1 Insights", body)


class PostFilterFormTests(TestCase):
    def test_invalid_date_range(self):
        form = PostFilterForm(data={"period": "custom", "start_date": "2026-03-20", "end_date": "2026-03-10"})
        self.assertFalse(form.is_valid())

    def test_valid_date_range(self):
        form = PostFilterForm(data={"period": "custom", "start_date": "2026-03-01", "end_date": "2026-03-10"})
        self.assertTrue(form.is_valid())
