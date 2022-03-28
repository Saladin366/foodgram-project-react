from django.core.exceptions import ValidationError

CHECK_TIME = 'Время приготовления должно быть больше нуля'
CHECK_AMOUNT = 'Ингредиент: Количество должно быть больше нуля'


def validate_time(value):
    if value <= 0:
        raise ValidationError(CHECK_TIME)
    return value


def validate_amount(value):
    if value <= 0:
        raise ValidationError(CHECK_AMOUNT)
    return value
