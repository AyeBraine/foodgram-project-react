from rest_framework import serializers


class MeNameNotInUsername:

    def __call__(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя \'me\' для поля username недоступно.'
            )
