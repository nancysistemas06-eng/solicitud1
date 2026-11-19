
from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),

    # REGISTRO
    path("nueva/", views.nueva_incidencia, name="nueva_incidencia"),

    # EXPORTACIÓN
    path("exportar/", views.exportar_excel, name="exportar_excel"),

    # ADMINISTRACIÓN
    path(
        "administrar/",
        views.administrar_incidencias,
        name="administrar_incidencias"
    ),

    path(
        "editar/<int:pk>/",
        views.editar_incidencia,
        name="editar_incidencia"
    ),

    path(
        "finalizar/<int:pk>/",
        views.finalizar_incidencia,
        name="finalizar_incidencia"
    ),

    path(
        "eliminar/<int:pk>/",
        views.eliminar_incidencia,
        name="eliminar_incidencia"
    ),
]
