"""
Вью для API рецептов.
"""

from core.models import Recipe
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """Вью для API рецептов."""

    serializer_class = serializers.RecipeDetailSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Recipe.objects.all().order_by('-id')

    def get_serializer_class(self):
        """Возвращает сериализатор класса, в зависимости от типа action."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Создание нового рецепта."""
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Удаление рецепта доступно только его автору."""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'detail': 'Вы можете удалить только свои рецепты.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
