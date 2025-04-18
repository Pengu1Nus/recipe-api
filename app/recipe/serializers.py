"""
Cериализаторы для рецептов.
"""

from core.models import Recipe
from rest_framework import serializers


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'cooking_time')
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """Сериализатор для рецептов конкретного рецепта."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('description', 'link')
