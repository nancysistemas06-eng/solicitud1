
from django.db import models
from django.conf import settings


# ==========================================
# SUCURSALES
# ==========================================

class Sucursal(models.Model):

    clave = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Clave de sucursal"
    )

    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre de sucursal"
    )

    activa = models.BooleanField(
        default=True,
        verbose_name="Sucursal activa"
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return f"{self.clave} - {self.nombre}"


# ==========================================
# PERFILES DE USUARIO
# ==========================================

class PerfilUsuario(models.Model):

    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Administrador de Sistemas"
        SUCURSAL = "SUCURSAL", "Usuario de sucursal"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil"
    )

    rol = models.CharField(
        max_length=15,
        choices=Roles.choices,
        default=Roles.SUCURSAL
    )

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios"
    )

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"
    
    def save(self, *args, **kwargs):

        if not self.folio:

            super().save(*args, **kwargs)

            self.folio = (
                f"INC-{self.creado_en:%Y}-{self.pk:05d}"
            )

            super().save(update_fields=["folio"])

            return

        super().save(*args, **kwargs)



# ==========================================
# INCIDENCIAS
# ==========================================

class Incidencia(models.Model):

    class Tipos(models.TextChoices):
        INCIDENCIA = "INCIDENCIA", "Incidencia"
        SOLICITUD = "SOLICITUD", "Solicitud"
        PENDIENTE = "PENDIENTE", "Actividad pendiente"

    class Prioridades(models.TextChoices):
        BAJA = "BAJA", "Baja"
        MEDIA = "MEDIA", "Media"
        ALTA = "ALTA", "Alta"
        CRITICA = "CRITICA", "Crítica"

    class Estados(models.TextChoices):
        NUEVA = "NUEVA", "Nueva"
        REVISION = "REVISION", "En revisión"
        PROCESO = "PROCESO", "En proceso"
        ESPERA = "ESPERA", "En espera"
        RESUELTA = "RESUELTA", "Resuelta"
        CERRADA = "CERRADA", "Cerrada"

    folio = models.CharField(
        max_length=25,
        unique=True,
        blank=True
    )

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="incidencias"
    )

    tipo = models.CharField(
        max_length=15,
        choices=Tipos.choices,
        default=Tipos.INCIDENCIA
    )

    categoria = models.CharField(
        max_length=80
    )

    titulo = models.CharField(
        max_length=150
    )

    descripcion = models.TextField()

    reportado_a = models.CharField(
        max_length=100,
        verbose_name="Responsable al que se reportó",
        blank=True
    )

    prioridad = models.CharField(
        max_length=10,
        choices=Prioridades.choices,
        default=Prioridades.MEDIA
    )

    estado = models.CharField(
        max_length=10,
        choices=Estados.choices,
        default=Estados.NUEVA
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="incidencias_creadas"
    )

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="incidencias_asignadas"
    )

    solucion = models.TextField(
        blank=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    resuelto_en = models.DateTimeField(
        null=True,
        blank=True
    )

    
    resuelto_en = models.DateTimeField(
        null=True,
        blank=True
    )

    resuelto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="incidencias_resueltas"
    )

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Incidencia"
        verbose_name_plural = "Incidencias"

        indexes = [
            models.Index(fields=["sucursal", "estado"]),
            models.Index(fields=["prioridad", "estado"]),
            models.Index(fields=["creado_en"]),
        ]

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if not self.folio:
            self.folio = (
                f"INC-{self.creado_en:%Y}-{self.pk:05d}"
            )

            super().save(update_fields=["folio"])




# ==========================================
# SEGUIMIENTO DE INCIDENCIAS
# ==========================================

class Seguimiento(models.Model):

    incidencia = models.ForeignKey(
        Incidencia,
        on_delete=models.CASCADE,
        related_name="seguimientos"
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="seguimientos_realizados"
    )

    estado_anterior = models.CharField(
        max_length=10,
        choices=Incidencia.Estados.choices,
        blank=True
    )

    estado_nuevo = models.CharField(
        max_length=10,
        choices=Incidencia.Estados.choices,
        blank=True
    )

    comentario = models.TextField()

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Seguimiento"
        verbose_name_plural = "Seguimientos"

    def __str__(self):
        return f"{self.incidencia.folio} - {self.fecha:%d/%m/%Y %H:%M}"
