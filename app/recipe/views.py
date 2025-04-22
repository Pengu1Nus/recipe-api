"""
Вью для API рецептов.
"""

from core.models import Ingredient, Recipe, Tag
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Список id тегов для фильтрации, '
                'разделенных запятыми',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Список id ингредиентов для фильтрации, '
                'разделенных запятыми',
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """Вью для API рецептов."""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def _params_to_ints(self, qs):
        """Преобразование строки параметров в целочисленные."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Получение рецептов для аутентифицированных юзеров."""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return (
            queryset.filter(user=self.request.user).order_by('-id').distinct()
        )

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT,
                enum=[0, 1],
                description='Фильтровать по элементам, назначенным рецептам.',
            ),
        ]
    )
)
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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return (
            queryset.filter(user=self.request.user)
            .order_by('-name')
            .distinct()
        )


class TagViewSet(BaseRecipeAttributesViewSet):
    """Управление тегами."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttributesViewSet):
    """Управление ингредиентами."""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
