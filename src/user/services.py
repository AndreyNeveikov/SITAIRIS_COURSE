from rest_framework.generics import get_object_or_404

from user.models import User


class AdminService:
    """
    A class that provides allowed actions for admin role.
    """

    def __init__(self, user_id):
        self.user = get_object_or_404(
            queryset=User.objects.prefetch_related('pages'),
            id=user_id
        )

    def toggle_block_status(self):
        """
        Toggles the block status for the user and all of his pages.
        """
        self.user.is_blocked = not self.user.is_blocked
        self.user.save()
        self.user.pages.all().update(is_blocked=self.user.is_blocked)

    def get_block_status_response(self) -> dict:
        """
        Returns the message for response, showing block status for the user.
        """
        message = {'status': {
            self.user.role: self.user.username,
            'blocked': self.user.is_blocked}
        }
        return message
