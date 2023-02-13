from django.contrib.auth.models import UserManager

from core.constants import Roles


class CustomUserManager(UserManager):
    def create_user(self, username, email=None, password=None,
                    role=Roles.USER.value, is_blocked=False):
        if not email:
            raise ValueError("Email is required.")
        if not username:
            raise ValueError("Username is required.")

        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.username = username
        user.role = role
        user.is_blocked = is_blocked

        if user.role == Roles.MODERATOR.value:
            user.is_staff = True
            user.is_superuser = False
            user.save()
            return user

        user.is_staff = True
        user.is_superuser = False
        user.save()
        return user

    def create_superuser(self, username: str, email: str = None, password: str = None,
                         role: str = Roles.ADMIN.value, is_blocked: bool = False):
        if not email:
            raise ValueError("Email is required.")
        if not username:
            raise ValueError("Username")

        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.username = username
        user.role = role
        user.is_blocked = is_blocked
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
