
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user

        # 👑 Admin users → admin panel
        if user.is_staff or user.is_superuser:
            return "/admin/"

        # 👤 Normal users → home page
        return "/"

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True

    def login_redirect_url(self, request):
        # 🔒 Prevent allauth from hijacking admin redirects
        if request.path.startswith("/admin"):
            return "/admin/"
        return super().login_redirect_url(request)
