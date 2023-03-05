from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsAuthAndNotBlocked
from page.models import Page
from page.serializers import PageSerializer
from user.models import User
from user.serializers import UserSerializer


class BaseSearch(GenericViewSet):
    filter_backends = [SearchFilter]
    permission_classes = [IsAuthAndNotBlocked]
    queryset_models_mapping = {
        Page: Page.objects.all(),
        User: User.objects.all()
    }
    search_fields_mapping = {
        Page: ('name', 'uuid', 'tags__name'),
        User: ('username', 'first_name')
    }
    serializer_models_mapping = {
        Page: PageSerializer,
        User: UserSerializer
    }

    def list(self, request, *args, **kwargs):
        search_results = {}
        for model, serializer in self.serializer_models_mapping.items():
            search_fields = self.search_fields_mapping.get(model)
            setattr(self, 'search_fields', search_fields)
            queryset = self.queryset_models_mapping.get(model)
            filtered_queryset = self.filter_queryset(queryset)
            serializer = serializer(instance=filtered_queryset,
                                    context=self.get_serializer_context(),
                                    many=True)
            search_results[model.__name__] = serializer.data
        return Response(data=search_results, status=status.HTTP_200_OK)
