# isort: skip_file
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
# from rest_framework.validators import UniqueValidator

from users.models import Follow, User
# from users.validators import MeNameNotInUsername


class UserReadSerializer(serializers.ModelSerializer):
    """ Сериализатор вывода профилей пользователей. """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request', False).user
        return (user.pk
                and Follow.objects.filter(user=user, following=obj).exists())


class UserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя. """
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password', 'id')
