# isort: skip_file
from django_filters import rest_framework as dfilters
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from api.pagination import AdjustablePagination
from api.permissions import AuthorAdminOrReadOnly
from api.serializers import (IngredientPageSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, TagSerializer)
from api.utils import flag_add_delete
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from users.models import User


class RecipeFilter(dfilters.FilterSet):
    """ Фильтр для вывода рецептов по query parameters. """
    tags = dfilters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        queryset=Tag.objects.all(),)
    author = dfilters.ModelChoiceFilter(queryset=User.objects.all())
    # is_favorited = dfilters.BooleanFilter(field_name='faved_by')
    # is_in_shopping_cart = dfilters.BooleanFilter(field_name='in_cart_for')

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)


class IngredientFilter(dfilters.FilterSet):
    """ Фильтр для вывода ингредиентов по query parameters. """
    name = dfilters.CharFilter(field_name='name',
                               lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeViewSet(viewsets.ModelViewSet):
    """ Вьюсет для вывода и фильтрации рецептов. """
    queryset = Recipe.objects.all()
    pagination_class = AdjustablePagination
    permission_classes = (permissions.AllowAny,)
    filter_backends = (dfilters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None and int(is_favorited) == 1:
            return Recipe.objects.filter(faved_by=self.request.user.id)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart is not None and int(is_in_shopping_cart) == 1:
            return Recipe.objects.filter(in_cart_for=self.request.user.id)
        return Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update',):
            return(AuthorAdminOrReadOnly(),)
        return super().get_permissions()

    @action(detail=True, permission_classes = (permissions.IsAuthenticated,),
            methods=('post', 'delete'))
    def favorite(self, request, pk):
        """ Добавление в Избранное и удаление оттуда. """
        return flag_add_delete(request, pk, Favorite)

    @action(detail=True, permission_classes = (permissions.IsAuthenticated,),
            methods=('post', 'delete'))
    def shopping_cart(self, request, pk):
        """ Добавление в Список покупок и удаление оттуда. """
        return flag_add_delete(request, pk, Cart)


class IngredientViewSet(viewsets.ModelViewSet):
    """ Вьюсет для вывода страницы со списком ингредиентов. """
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientPageSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_class = (IngredientFilter,)


class TagViewSet(viewsets.ModelViewSet):
    """ Вьюсет для вывода списка тегов. """
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
