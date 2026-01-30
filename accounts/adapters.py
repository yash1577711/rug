from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True

    def login_allowed(self, user):
        # Allow admin/staff users WITHOUT email verification
        if user.is_staff or user.is_superuser:
            return True

        # Normal users MUST have verified email
        return super().login_allowed(user)
