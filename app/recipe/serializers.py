"""
Cериализаторы для рецептов.
"""

from core.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')
        read_only_fields = ('id',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор связи ингредиента с рецептом"""

    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')


class IngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор представления Ингредиента для Рецепта"""

    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('name',)
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientGetSerializer(
        source='recipeingredient_set', many=True, read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'title',
            'description',
            'cooking_time',
            'ingredients',
            'tags',
            'image',
        )
        read_only_fields = ('id',)

    def _get_or_create_tags(self, tags, recipe):
        """Функция для получения или обновления тега."""

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                **tag,
            )
            recipe.tags.add(tag_obj)
        return recipe

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Функция для получения или обновления ингредиента."""
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)
        return recipe

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Сериализатор для рецептов конкретного рецепта."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + (
            'link',
            'ingredients',
        )


class RecipeImageSerializer(serializers.ModelSerializer):
    """Сериализатор для загрузки изображений."""

    class Meta:
        model = Recipe
        fields = ('image',)
        read_only_fields = ('id',)
        extra_kwargs = {'image': {'required': 'True'}}
