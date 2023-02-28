from core.constants import Roles
from page.serializers import (PageOwnerSerializer, PageSerializer,
                              FullPageSerializer)


class SerializerActionMixin:
    def get_serializer_class(self):
        if self.action == 'create':
            return self.serializer_action_classes.get(self.action)
        if self.request.user.role in (Roles.MODERATOR.value,
                                      Roles.ADMIN.value):
            return FullPageSerializer
        if self.request.user == self.get_object().owner:
            return PageOwnerSerializer
        return self.serializer_action_classes.get(self.action, PageSerializer)
