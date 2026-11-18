
from django.contrib import admin
from .models import Sucursal, PerfilUsuario, Incidencia, Seguimiento


# ==========================================
# SUCURSALES
# ==========================================

@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):

    list_display = (
        "clave",
        "nombre",
        "activa",
    )

    list_filter = (
        "activa",
    )

    search_fields = (
        "clave",
        "nombre",
    )


# ==========================================
# PERFILES DE USUARIO
# ==========================================

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):

    list_display = (
        "usuario",
        "rol",
        "sucursal",
    )

    list_filter = (
        "rol",
        "sucursal",
    )

    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "sucursal__nombre",
    )


# ==========================================
# SEGUIMIENTOS
# ==========================================

class SeguimientoInline(admin.TabularInline):

    model = Seguimiento
    extra = 0
    readonly_fields = (
        "usuario",
        "estado_anterior",
        "estado_nuevo",
        "comentario",
        "fecha",
    )

    can_delete = False


# ==========================================
# INCIDENCIAS
# ==========================================

@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):

    list_display = (
        "folio",
        "titulo",
        "sucursal",
        "tipo",
        "prioridad",
        "estado",
        "responsable",
        "creado_en",
    )

    list_filter = (
        "sucursal",
        "tipo",
        "prioridad",
        "estado",
    )

    search_fields = (
        "folio",
        "titulo",
        "descripcion",
        "sucursal__nombre",
    )

    readonly_fields = (
        "folio",
        "creado_en",
        "actualizado_en",
        "resuelto_en",
    )

    inlines = [
        SeguimientoInline,
    ]

    list_per_page = 25


# ==========================================
# ADMINISTRACIÓN DE SEGUIMIENTOS
# ==========================================

@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):

    list_display = (
        "incidencia",
        "usuario",
        "estado_anterior",
        "estado_nuevo",
        "fecha",
    )

    list_filter = (
        "estado_anterior",
        "estado_nuevo",
        "fecha",
    )

    search_fields = (
        "incidencia__folio",
        "comentario",
        "usuario__username",
    )

    readonly_fields = (
        "fecha",
    )
