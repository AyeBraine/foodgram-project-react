from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r'^[\w.@+-]+\Z'
    message = (
        'Имя пользователя может содержать только буквы латинского алфавита, '
        'цифры и следующие символы: @/./+/-/_.'
    )
    flags = 0
