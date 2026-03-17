from django import forms

from .models import BlogPost, LinkedInPost, Project, ResearchPaper, UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["full_name", "role_title", "linkedin_profile_url", "about", "profile_picture"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "role_title": forms.TextInput(attrs={"placeholder": "Role / team (required)"}),
            "linkedin_profile_url": forms.URLInput(attrs={"placeholder": "https://www.linkedin.com/in/your-profile"}),
            "about": forms.Textarea(attrs={"rows": 3, "placeholder": "Short intro about your work"}),
        }


class LinkedInPostForm(forms.ModelForm):
    class Meta:
        model = LinkedInPost
        fields = ["post_title", "company_name", "posted_at", "post_url", "notes"]
        widgets = {
            "post_title": forms.TextInput(attrs={"placeholder": "LinkedIn post title"}),
            "company_name": forms.TextInput(attrs={"placeholder": "Company name"}),
            "posted_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "post_url": forms.URLInput(attrs={"placeholder": "https://www.linkedin.com/posts/..."}),
            "notes": forms.Textarea(attrs={"rows": 2, "placeholder": "Optional notes"}),
        }


class PostFilterForm(forms.Form):
    PERIOD_CHOICES = [
        ("all", "Any time"),
        ("last_7_days", "Last 7 days"),
        ("last_30_days", "Last 30 days"),
        ("custom", "Custom range"),
    ]

    q = forms.CharField(
        required=False,
        label="Keyword",
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "Title, company, notes"}),
    )
    period = forms.ChoiceField(required=False, choices=PERIOD_CHOICES, initial="all")
    company_name = forms.CharField(required=False, label="Company", max_length=255)
    user_name = forms.CharField(required=False, label="User", max_length=255)
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned_data = super().clean()
        period = cleaned_data.get("period") or "all"
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if cleaned_data.get("q"):
            cleaned_data["q"] = cleaned_data["q"].strip()

        if period == "custom":
            if not start_date or not end_date:
                raise forms.ValidationError("For custom range, provide both start and end dates.")
            if start_date > end_date:
                raise forms.ValidationError("Start date cannot be after end date.")

        return cleaned_data


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "start_date", "end_date"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Project name"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Project summary"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "platform", "published_on", "url", "summary"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Blog post title"}),
            "platform": forms.TextInput(attrs={"placeholder": "Medium / Dev.to / Personal site"}),
            "published_on": forms.DateInput(attrs={"type": "date"}),
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "summary": forms.Textarea(attrs={"rows": 3, "placeholder": "Short summary"}),
        }


class ResearchPaperForm(forms.ModelForm):
    class Meta:
        model = ResearchPaper
        fields = ["title", "publication", "published_on", "url", "abstract"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Paper title"}),
            "publication": forms.TextInput(attrs={"placeholder": "Journal / Conference"}),
            "published_on": forms.DateInput(attrs={"type": "date"}),
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "abstract": forms.Textarea(attrs={"rows": 4, "placeholder": "Key findings or abstract"}),
        }
