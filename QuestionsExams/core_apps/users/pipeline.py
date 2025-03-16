def complete_profile(backend, details, response, user=None, *args, **kwargs):
    """
    Ensure the user has a complete profile after social login.
    """
    if user:
        user.first_name = details.get("first_name", "Default")
        user.last_name = details.get("last_name", "User")
        user.set_unusable_password()  # If no password is provided, make it unusable
        user.save()
    return {"user": user}