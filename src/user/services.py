from rest_framework.generics import get_object_or_404

from user.models import User


class AdminService:
    """
    A class that provides allowed actions for admin role.
    """
    def __init__(self, user_id):
        self.user = get_object_or_404(User, id=user_id)

    def toggle_block_status(self):
        """
        Toggles the block status for the user.
        """
        self.user.is_blocked = not self.user.is_blocked
        self.user.save()

    def get_block_status_response(self) -> dict:
        """
        Returns the message for response, showing block status for the user.
        """
        message = '{}: {}. Blocked: {}'.format(
            self.user.role.title(), self.user.username, self.user.is_blocked
        )
        status = 'status'
        return {status: message}
