from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "cedula",
            "telefono",
            "rol",
        )


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    add_form = UsuarioCreationForm

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "cedula",
        "rol",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "cedula",
        "first_name",
        "last_name",
    )

    list_filter = (
        "rol",
        "is_active",
        "is_staff",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Información adicional",
            {
                "fields": (
                    "cedula",
                    "telefono",
                    "rol",
                )
            }
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "cedula",
                    "telefono",
                    "rol",
                    "password1",
                    "password2",
                ),
            },
        ),
    )