# isort: skip_file
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, ReciIngredi, Recipe, Tag
from users.models import Follow
from users.serializers import UserReadSerializer


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор тегов. """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientPageSerializer(serializers.ModelSerializer):
    """ Сериализатор для ингредиентов. """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ReciIngrediReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для вывода ингредиентов по get. """
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = ReciIngredi
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReciIngrediWriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для create/update рецептов, мини-формат. """
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.IntegerField(write_only=True, min_value=1)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all())

    class Meta:
        model = ReciIngredi
        fields = ('id', 'amount', 'recipe')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """ Сериализатор для вывода страницы «Мои подписки». """
    id = serializers.ReadOnlyField(source='following.id')
    email = serializers.ReadOnlyField(source='following.email')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='following.recipes.count')

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        """ Возвращает True, если есть подписка. """
        return Follow.objects.filter(
            user=obj.user, following=obj.following).exists()

    def get_recipes(self, obj):
        """ Выводит заданное число рецептов автора в его карточке. """
        request = self.context['request']
        rec_limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(
            author=obj.following).order_by('-pub_date')
        if rec_limit:
            queryset = queryset[:int(rec_limit)]
        return RecipeMiniSerializer(queryset, many=True).data


class RecipeMiniSerializer(serializers.ModelSerializer):
    """ Сериализатор миниформата рецепта (для Favs и Cart). """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['name', 'image', 'cooking_time']


class RecipeReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для GET-запросов рецептов. """
    tags = TagSerializer(many=True, read_only=True)
    author = UserReadSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')
        read_only_fields = ('id', 'author',)

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None and int(is_favorited) == 1:
            return Recipe.objects.filter(faved_by__id=self.request.user.pk)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart is not None and int(is_in_shopping_cart) == 1:
            return Recipe.objects.filter(in_cart_for__id=self.request.user.pk)
        return Recipe.objects.all()

    def get_is_favorited(self, obj):
        """ Возвращает True, если рецепт в списке покупок. """
        user = self.context['request'].user
        return user.pk and obj.faved_by.filter(id=user.pk).exists()

    def get_is_in_shopping_cart(self, obj):
        """ Возвращает True, если рецепт в списке покупок. """
        user = self.context['request'].user
        return user.pk and obj.in_cart_for.filter(id=user.pk).exists()

    def get_ingredients(self, obj):
        rec_ings = ReciIngredi.objects.filter(recipe=obj)
        return ReciIngrediReadSerializer(rec_ings, many=True).data

    def validate_cooking_time(self, value):
        """ Время приготовления не более ~2 суток (некоторые супы). """
        if 0 < value < 3000:
            return value
        raise ValidationError('Время приготовления: недопустимое значение!')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для POST/PATCH-запросов рецептов. """
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = ReciIngrediWriteSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    author = UserReadSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')
        read_only_fields = ('id', 'author', 'tags')

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Проверьте, какой-то ингредиент был выбран более 1 раза'
            )
        return data

    def create(self, validated_data):
        """ Создаёт вложенные сериализаторы tag и ingredient. """
        current_user = self.context['request'].user
        if not current_user.pk:
            raise serializers.ValidationError('Пользователя не существует.')
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=current_user, **validated_data)
        recipe.tags.set(tags_data)
        ing_bulk_data = (
            ReciIngredi(ingredient=ing['ingredient'],
                        recipe=recipe,
                        amount=ing['amount'])
            for ing in ingredients_data)
        ReciIngredi.objects.bulk_create(ing_bulk_data)
        return recipe

    def update(self, instance, validated_data):
        """ Переписывает целиком вложенные сериализаторы tag и ingredient. """
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        current_ings = ReciIngredi.objects.filter(recipe=instance.id)
        current_ings.delete()
        ing_bulk_data = (
            ReciIngredi(ingredient=ing['ingredient'],
                        recipe=instance,
                        amount=ing['amount'])
            for ing in ingredients_data)
        ReciIngredi.objects.bulk_create(ing_bulk_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['ingredients'] = ReciIngrediReadSerializer(
            ReciIngredi.objects.filter(recipe=instance), many=True
        ).data
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        return representation
