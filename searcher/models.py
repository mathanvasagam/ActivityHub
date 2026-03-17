from django.conf import settings
from django.db import models


class SearchQuery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_url = models.URLField()
    hashtag = models.CharField(max_length=100)
    profile_name = models.CharField(max_length=255, blank=True)
    total_posts = models.IntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-searched_at"]

    def __str__(self) -> str:
        return f"{self.profile_name or self.profile_url} [{self.hashtag}]"


class PostResult(models.Model):
    query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name="posts")
    post_url = models.URLField()
    post_date = models.DateField(null=True, blank=True)
    snippet = models.TextField(blank=True)

    class Meta:
        ordering = ["-post_date", "id"]

    def __str__(self) -> str:
        return self.post_url


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255)
    role_title = models.CharField(max_length=255)
    linkedin_profile_url = models.URLField()
    about = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.user.username})"


class LinkedInPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="linkedin_posts")
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="posts")
    post_title = models.CharField(max_length=300)
    company_name = models.CharField(max_length=255)
    posted_at = models.DateTimeField()
    post_url = models.URLField(unique=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-posted_at"]

    def __str__(self) -> str:
        return f"{self.post_title} - {self.company_name}"


class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class BlogPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blog_posts")
    title = models.CharField(max_length=255)
    platform = models.CharField(max_length=120, blank=True)
    url = models.URLField(unique=True)
    published_on = models.DateField(null=True, blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_on", "-created_at"]

    def __str__(self) -> str:
        return self.title


class ResearchPaper(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="research_papers")
    title = models.CharField(max_length=300)
    publication = models.CharField(max_length=255, blank=True)
    url = models.URLField(unique=True)
    published_on = models.DateField(null=True, blank=True)
    abstract = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_on", "-created_at"]

    def __str__(self) -> str:
        return self.title
