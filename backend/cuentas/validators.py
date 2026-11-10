import re
from django.core.exceptions import ValidationError


def validar_cedula(cedula):
    cedula = str(cedula)

    if not re.fullmatch(r"[0-9]{10}", cedula):
        raise ValidationError(
            "La cédula debe tener exactamente 10 dígitos."
        )

    provincia = int(cedula[:2])

    if not (1 <= provincia <= 24 or provincia == 30):
        raise ValidationError(
            "El código de provincia no es válido."
        )

    if int(cedula[2]) > 5:
        raise ValidationError(
            "El tercer dígito de la cédula no es válido."
        )

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0

    for i in range(9):
        producto = int(cedula[i]) * coeficientes[i]

        if producto >= 10:
            producto -= 9

        suma += producto

    digito_verificador = (10 - (suma % 10)) % 10

    if digito_verificador != int(cedula[9]):
        raise ValidationError(
            "La cédula tiene un dígito verificador incorrecto."
        )


def validar_telefono(telefono):
    if not re.fullmatch(r"09[0-9]{8}", telefono):
        raise ValidationError(
            "Ingresa un celular ecuatoriano válido de 10 dígitos."
        )