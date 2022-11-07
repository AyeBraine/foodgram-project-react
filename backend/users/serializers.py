# isort: skip_file
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import Follow, User
from users.validators import MeNameNotInUsername


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


class UserSuccessSerializer(serializers.ModelSerializer):
    """ Сериализатор вывода профилей пользователей. """
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class UserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя. """
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password', 'id')

    # email = serializers.EmailField(
    #     max_length=254,
    #     validators=(UniqueValidator(queryset=User.objects.all()),)
    # )
    # username = serializers.CharField(
    #     max_length=64,
    #     validators=(
    #         UniqueValidator(queryset=User.objects.all()),
    #         MeNameNotInUsername()
    #     )
    # )
    # first_name = serializers.CharField(max_length=150)
    # last_name = serializers.CharField(max_length=150)
    # password = serializers.CharField()

    # def create(self, validated_data):
    #     password = validated_data.pop('password', None)
    #     instance = self.Meta.model(**validated_data)
    #     if password is not None:
    #         instance.set_password(password)
    #     instance.save()
    #     return instance

    # def update(self, instance, validated_data):
    #     for attr, value in validated_data.items():
    #         if attr == 'password':
    #             instance.set_password(value)
    #         else:
    #             setattr(instance, attr, value)
    #     instance.save()
    #     return instance
