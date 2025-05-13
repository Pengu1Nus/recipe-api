"""
Вью для API рецептов.
"""

from core.models import Ingredient, Recipe, Tag
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipe import filters, serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """Вью для API рецептов."""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags', 'ingredients')
    filterset_class = filters.RecipeFilter

    def destroy(self, request, *args, **kwargs):
        """Удаление рецепта доступно только его автору."""

        instance = self.get_object()

        if instance.user != request.user:
            return Response(
                {'detail': 'Вы можете удалить только свои рецепты.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Возвращает сериализатор класса, в зависимости от типа action."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Создание нового рецепта."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Загрузка изображения рецепта."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttributesViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый вьюсет для тегов и ингредиентов."""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Фильтр для аутентифицированных пользователей."""
        return (
            # self.queryset.filter(user=self.request.user)
            # self.queryset.filter(name=self.request.name)
            self.queryset.all().order_by('-name').distinct()
        )


class TagViewSet(BaseRecipeAttributesViewSet):
    """Управление тегами."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttributesViewSet):
    """Управление ингредиентами."""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = PageNumberPagination
