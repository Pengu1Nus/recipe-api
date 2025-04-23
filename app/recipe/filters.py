from core.models import Recipe
from django_filters import rest_framework as filters


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__name', lookup_expr='iexact')
    ingredients = filters.CharFilter(
        field_name='ingredients__name', lookup_expr='iexact'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'ingredients']
