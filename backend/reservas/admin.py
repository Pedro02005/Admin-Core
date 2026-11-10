from django.contrib import admin
from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "cliente",
        "cancha",
        "inicio",
        "fin",
        "estado",
        "total",
    )

    list_filter = (
        "estado",
        "cancha__complejo",
    )

    search_fields = (
        "cliente__username",
        "cancha__nombre",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False