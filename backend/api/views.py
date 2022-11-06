# isort: skip_file
from django_filters import rest_framework as dfilters
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action

from api.pagination import AdjustablePagination
from api.permissions import AuthorAdminOrReadOnly
from api.serializers import (IngredientPageSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, TagSerializer)
from api.utils import flag_add_delete
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag


class RecipeFilter(dfilters.FilterSet):
    """ Фильтр для вывода рецептов по query parameters. """
    author = dfilters.CharFilter(field_name='author__id')
    tags = dfilters.CharFilter(
        field_name='tags__slug', lookup_expr='icontains')
    is_favorited = dfilters.BooleanFilter(field_name='faved_by')
    is_in_shopping_cart = dfilters.BooleanFilter(field_name='in_cart_for')

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Вьюсет для вывода и фильтрации рецептов. """
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = (AuthorAdminOrReadOnly,)
    pagination_class = AdjustablePagination
    filter_backends = (dfilters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, permission_classes=(permissions.IsAuthenticated,),
            methods=('post', 'delete'))
    def favorite(self, request, pk):
        """ Добавление в Избранное и удаление оттуда. """
        return flag_add_delete(request, pk, Favorite)

    @action(detail=True, permission_classes=(permissions.IsAuthenticated,),
            methods=('post', 'delete'))
    def shopping_cart(self, request, pk):
        """ Добавление в Список покупок и удаление оттуда. """
        return flag_add_delete(request, pk, Cart)


class IngredientViewSet(viewsets.ModelViewSet):
    """ Вьюсет для вывода страницы со списком ингредиентов. """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientPageSerializer
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    """ Вьюсет для вывода списка тегов. """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
