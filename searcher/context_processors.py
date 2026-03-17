def portal_context(request):
    mode = "guest"
    avatar_url = ""
    avatar_initials = "U"

    if request.user.is_authenticated:
        mode = "admin" if request.user.is_staff else "user"

        first = (request.user.first_name or "").strip()
        last = (request.user.last_name or "").strip()
        if first and last:
            avatar_initials = f"{first[0]}{last[0]}".upper()
        elif first:
            avatar_initials = first[:2].upper()
        else:
            avatar_initials = (request.user.username or "U")[:2].upper()

        try:
            profile = request.user.profile
        except Exception:
            profile = None
        if profile and getattr(profile, "profile_picture", None):
            try:
                avatar_url = profile.profile_picture.url
            except Exception:
                avatar_url = ""

    return {
        "portal_mode": mode,
        "header_avatar_url": avatar_url,
        "header_avatar_initials": avatar_initials,
    }
