from rest_framework import serializers

from complejos.models import Cancha


class ConsultaDisponibilidadSerializer(serializers.Serializer):

    fecha = serializers.DateField()

    duracion = serializers.IntegerField(
        min_value=60,
        max_value=180
    )

    def validate_duracion(self, value):
        if value % 30 != 0:
            raise serializers.ValidationError(
                "La duración debe ser múltiplo de 30."
            )

        return value


class CotizacionSerializer(serializers.Serializer):

    cancha_id = serializers.PrimaryKeyRelatedField(
        queryset=Cancha.objects.all(),
        source="cancha"
    )

    inicio = serializers.DateTimeField()
    fin = serializers.DateTimeField()

    def validate(self, attrs):
        if attrs["inicio"] >= attrs["fin"]:
            raise serializers.ValidationError(
                "El inicio debe ser anterior al fin."
            )

        return attrs