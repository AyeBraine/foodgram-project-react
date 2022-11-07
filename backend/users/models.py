# isort: skip_file
from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.validators import UnicodeUsernameValidator


class User(AbstractUser):
    """ Кастом-модель пользователя. """
    USER_ROLES = (
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    )

    username = models.CharField(
        'username',
        max_length=150,
        blank=False,
        unique=True,
        help_text=(
            'Не больше 150 знаков, допустимы только '
            'буквы латинского алфавита, цифры и символы.'),
        validators=(UnicodeUsernameValidator,),
        error_messages={
            'unique': ('Пользователь с таким именем уже существует.'),
        },
    )
    password = models.CharField('Пароль', max_length=150)
    first_name = models.CharField('Имя', max_length=150, blank=False,)
    last_name = models.CharField('Фамилия', max_length=150, blank=False,)
    email = models.EmailField(
        'E-mail', blank=False, unique=True,
        error_messages={
            'unique': ('Пользователь с таким адресом e-mail уже существует.'),
        },
    )
    role = models.CharField(max_length=15, choices=USER_ROLES, default='user')

    class Meta:
        ordering = ('username',)

    @property
    def is_user_role(self):
        """ Метод вывода прав доступа пользователя. """
        return self.role == self.USER_ROLES[0][0]

    @property
    def is_admin_role(self):
        """ Метод вывода прав доступа пользователя. """
        return self.role == self.USER_ROLES[1][0]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='has_follower')

    def __str__(self):
        return f'подписка на {self.following}'
