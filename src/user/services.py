from rest_framework.generics import get_object_or_404

from user.models import User


class AdminService:
    def __init__(self, user_id):
        self.user = get_object_or_404(User, id=user_id)

    def block_user(self):
        self.user.is_blocked = not self.user.is_blocked
        self.user.save()

    def get_message(self):
        message = f'User: {self.user.username}. '\
                  f'Blocked: {self.user.is_blocked}'
        return message
