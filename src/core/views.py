from rest_framework import mixins, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from page.models import Page
from page.serializers import PageSerializer
from user.models import User
from user.serializers import UserSerializer


class BaseSearch(mixins.ListModelMixin,
                 GenericViewSet):
    serializer_models_mapping = {
        Page: PageSerializer,
        User: UserSerializer
    }
    search_fields_mapping = {
        Page: ('name', 'uuid', 'tags__name'),
        User: ('username', 'first_name')
    }

    def list(self, request, *args, **kwargs):
        search_results = {}
        search_filter = SearchFilter()
        for model, serializer in self.serializer_models_mapping.items():
            search_fields = self.search_fields_mapping.get(model)
            setattr(self, 'search_fields', search_fields)
            filtered_queryset = search_filter.filter_queryset(
                request=request, queryset=model.objects.all(), view=self
            )
            serializer = serializer(instance=filtered_queryset,
                                    context={'request': request},
                                    many=True)
            search_results[model.__name__] = serializer.data
        return Response(data=search_results, status=status.HTTP_200_OK)
