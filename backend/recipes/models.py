# isort: skip_file
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class TagLowerField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(TagLowerField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).lower()


class Ingredient(models.Model):
    """ Модель для ингредиентов блюд. """
    name = models.CharField('Ингредиент', max_length=256)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        ordering = ('name',)
        constraints = (models.UniqueConstraint(
                       fields=('name', 'measurement_unit'),
                       name='unique_ingredi_check'),)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = TagLowerField(max_length=64, verbose_name='Имя', unique=True)
    color = models.CharField(max_length=7, verbose_name='Цвет (#hex)',)
    slug = models.SlugField(max_length=32, unique=True)

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    """ Модель для пользовательских рецептов. """
    author = models.ForeignKey(
        User, verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE)
    name = models.CharField('Название', max_length=512)
    image = models.ImageField('Фотография', upload_to='recipes/', blank=False)
    text = models.TextField(
        'Описание', max_length=6000,
        help_text='Дайте общее описание рецепта, а затем перечислите '
                  'порядок действий при приготовлении блюда.')

    ingredients = models.ManyToManyField(
        Ingredient, through='ReciIngredi', related_name='recipes',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag, related_name='recipe', verbose_name='Теги',)

    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1, message='Не менее 1 минуты!'),
                    MaxValueValidator(3000, message='Не больше 2 дней!')),
        verbose_name='Время приготовления (мин.)')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    faved_by = models.ManyToManyField(
        User, through='Favorite', related_name='favorited',
        verbose_name='В избранном у')
    in_cart_for = models.ManyToManyField(
        User, through='Cart', related_name='in_cart',
        verbose_name='В списке покупок у')

    class Meta:
        ordering = ('-pub_date',)
        constraints = (models.UniqueConstraint(fields=('author', 'name'),
                                               name='unique_recipe_check'),)

    def __str__(self):
        return self.name


class ReciIngredi(models.Model):
    """ Through-модель для рецептов/ингредиентов. """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    # количество в этой связке рецепт-ингредиент
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1, message='Не менее 1 ед.'),)
    )

    def __str__(self):
        return f'{self.ingredient} в рецепте {self.recipe}'


class Favorite(models.Model):
    """ Through-модель для добавления в избранное. """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = (models.UniqueConstraint(fields=('user', 'recipe'),
                                               name='unique_fav_check'),)

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в Избранное.'


class Cart(models.Model):
    """ Through-модель для списка покупок. """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = (models.UniqueConstraint(fields=('user', 'recipe'),
                                               name='unique_cart_check'),)

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок.'
