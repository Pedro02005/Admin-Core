from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower

from decimal import Decimal

class Complejo(models.Model):

    nombre = models.CharField(max_length=100)

    descripcion = models.TextField(
        blank=True
    )

    ciudad = models.CharField(max_length=100)

    direccion = models.CharField(max_length=200)

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Complejo"
        verbose_name_plural = "Complejos"

        constraints = [
            models.UniqueConstraint(
                Lower("nombre"),
                Lower("ciudad"),
                name="complejo_nombre_ciudad_unicos"
            )
        ]

    def clean(self):
        super().clean()

        for campo in ["nombre", "ciudad", "direccion"]:
            valor = getattr(self, campo)

            if valor is not None:
                setattr(self, campo, valor.strip())

            if not getattr(self, campo):
                raise ValidationError({
                    campo: "Este campo no puede estar vacío."
                })

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"


class Cancha(models.Model):

    DEPORTES = [
        ("FUTBOL", "Fútbol"),
        ("BASQUET", "Básquet"),
        ("VOLEY", "Vóley"),
        ("TENIS", "Tenis"),
        ("PADEL", "Pádel"),
    ]

    complejo = models.ForeignKey(
        Complejo,
        on_delete=models.PROTECT,
        related_name="canchas"
    )

    nombre = models.CharField(max_length=100)

    deporte = models.CharField(
        max_length=20,
        choices=DEPORTES
    )

    capacidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cancha"
        verbose_name_plural = "Canchas"

        constraints = [
            models.UniqueConstraint(
                Lower("nombre"),
                "complejo",
                name="cancha_nombre_complejo_unicos"
            ),

            models.CheckConstraint(
                condition=models.Q(capacidad__gte=1),
                name="cancha_capacidad_minima"
            )
        ]

    def clean(self):
        super().clean()

        if self.nombre is not None:
            self.nombre = self.nombre.strip()

        if not self.nombre:
            raise ValidationError({
                "nombre": "El nombre de la cancha es obligatorio."
            })

    def __str__(self):
        return f"{self.nombre} - {self.complejo.nombre}"
    
    
   
    
    
class HorarioAtencion(models.Model):

    DIAS = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.PROTECT,
        related_name="horarios"
    )

    dia_semana = models.IntegerField(choices=DIAS)

    apertura = models.TimeField()
    cierre = models.TimeField()

    class Meta:
        verbose_name = "Horario de atención"
        verbose_name_plural = "Horarios de atención"
        ordering = ["cancha", "dia_semana", "apertura"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(apertura__lt=models.F("cierre")),
                name="horario_apertura_menor_cierre"
            )
        ]

    def clean(self):
        super().clean()

        if not all([
            self.cancha_id is not None,
            self.dia_semana is not None,
            self.apertura is not None,
            self.cierre is not None,
        ]):
            return

        if self.apertura >= self.cierre:
            raise ValidationError(
                "La apertura debe ser anterior al cierre."
            )

        horarios = HorarioAtencion.objects.filter(
            cancha_id=self.cancha_id,
            dia_semana=self.dia_semana,
            apertura__lt=self.cierre,
            cierre__gt=self.apertura,
        ).exclude(pk=self.pk)

        if horarios.exists():
            raise ValidationError(
                "Ya existe un horario que se superpone "
                "para esta cancha y día."
            )

    def __str__(self):
        return (
            f"{self.cancha} - "
            f"{self.get_dia_semana_display()} "
            f"{self.apertura:%H:%M}-{self.cierre:%H:%M}"
        )    
        
        
################################
class Tarifa(models.Model):

    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.PROTECT,
        related_name="tarifas"
    )

    dia_semana = models.IntegerField(
        choices=HorarioAtencion.DIAS
    )

    inicio = models.TimeField()
    fin = models.TimeField()

    valor_hora = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tarifa"
        verbose_name_plural = "Tarifas"
        ordering = ["cancha", "dia_semana", "inicio"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(inicio__lt=models.F("fin")),
                name="tarifa_inicio_menor_fin"
            ),
            models.CheckConstraint(
                condition=models.Q(valor_hora__gt=0),
                name="tarifa_valor_positivo"
            ),
        ]

    def clean(self):
        super().clean()

        if not all([
            self.cancha_id is not None,
            self.dia_semana is not None,
            self.inicio is not None,
            self.fin is not None,
        ]):
            return

        if self.inicio >= self.fin:
            raise ValidationError(
                "El inicio debe ser anterior al fin."
            )

        if not self.activa:
            return

        tarifas = Tarifa.objects.filter(
            cancha_id=self.cancha_id,
            dia_semana=self.dia_semana,
            activa=True,
            inicio__lt=self.fin,
            fin__gt=self.inicio,
        ).exclude(pk=self.pk)

        if tarifas.exists():
            raise ValidationError(
                "Ya existe una tarifa activa que se "
                "superpone para esta cancha y día."
            )

    def __str__(self):
        return (
            f"{self.cancha} - "
            f"{self.get_dia_semana_display()} - "
            f"${self.valor_hora}/hora"
        )
    


class Bloqueo(models.Model):

    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.PROTECT,
        related_name="bloqueos"
    )

    administrador = models.ForeignKey(
        "cuentas.Usuario",
        on_delete=models.PROTECT,
        related_name="bloqueos_creados"
    )

    inicio = models.DateTimeField()
    fin = models.DateTimeField()

    motivo = models.CharField(max_length=200)

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Bloqueo"
        verbose_name_plural = "Bloqueos"
        ordering = ["-inicio"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(inicio__lt=models.F("fin")),
                name="bloqueo_inicio_menor_fin"
            )
        ]

    def clean(self):
        super().clean()

        if not self.motivo or not self.motivo.strip():
            raise ValidationError({
                "motivo": "El motivo es obligatorio."
            })

        self.motivo = self.motivo.strip()

        if not all([
            self.cancha_id is not None,
            self.inicio is not None,
            self.fin is not None,
        ]):
            return

        if self.inicio >= self.fin:
            raise ValidationError(
                "La fecha de inicio debe ser "
                "anterior a la fecha de fin."
            )

        if not self.activo:
            return

        bloqueos = Bloqueo.objects.filter(
            cancha_id=self.cancha_id,
            activo=True,
            inicio__lt=self.fin,
            fin__gt=self.inicio,
        ).exclude(pk=self.pk)

        if bloqueos.exists():
            raise ValidationError(
                "Ya existe un bloqueo activo que se "
                "superpone con estas fechas."
            )

    def __str__(self):
        return f"{self.cancha} - {self.motivo}"