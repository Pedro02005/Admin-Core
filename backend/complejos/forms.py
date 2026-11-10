from django import forms
from django.urls import reverse

from .models import Complejo, Cancha, Tarifa


class TarifaAdminForm(forms.ModelForm):

    complejo = forms.ModelChoiceField(
        queryset=Complejo.objects.all(),
        label="Complejo deportivo",
        empty_label="Seleccione un complejo"
    )

    class Meta:
        model = Tarifa
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["complejo"].widget.attrs["data-canchas-url"] = reverse(
            "admin:complejos_tarifa_canchas"
        )
        self.fields["cancha"].empty_label = "Seleccione una cancha"
        if self.instance.cancha_id:
            self.initial.setdefault("complejo", self.instance.cancha.complejo_id)

        complejo_id = self["complejo"].value()
        canchas = Cancha.objects.none()
        if complejo_id and str(complejo_id).isascii() and str(complejo_id).isdigit():
            canchas = Cancha.objects.filter(complejo_id=complejo_id).order_by("nombre")

        self.fields["cancha"].queryset = canchas
