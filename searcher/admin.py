from django.contrib import admin

from .models import LinkedInPost, PostResult, SearchQuery, UserProfile


class PostResultInline(admin.TabularInline):
    model = PostResult
    extra = 0


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "profile_name", "hashtag", "total_posts", "searched_at")
    list_filter = ("hashtag", "searched_at")
    search_fields = ("profile_name", "profile_url", "user__username")
    inlines = [PostResultInline]


@admin.register(PostResult)
class PostResultAdmin(admin.ModelAdmin):
    list_display = ("id", "query", "post_url", "post_date")
    search_fields = ("post_url", "snippet")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "role_title", "linkedin_profile_url", "updated_at")
    search_fields = ("full_name", "user__username", "linkedin_profile_url", "role_title")


@admin.register(LinkedInPost)
class LinkedInPostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "company_name", "post_title", "posted_at")
    list_filter = ("company_name", "posted_at")
    search_fields = ("post_title", "company_name", "user__username", "post_url")
