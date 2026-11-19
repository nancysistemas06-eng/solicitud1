
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from .models import Incidencia, PerfilUsuario, Seguimiento
from .forms import IncidenciaForm, AdministrarIncidenciaForm


# ==========================================
# OBTENER PERFIL DEL USUARIO
# ==========================================

def obtener_perfil(usuario):

    try:
        return usuario.perfil

    except PerfilUsuario.DoesNotExist:
        raise PermissionDenied(
            "Tu usuario no tiene un perfil configurado. "
            "Contacta al administrador de Sistemas."
        )


# ==========================================
# VERIFICAR QUE SEA ADMINISTRADOR
# ==========================================

def verificar_administrador(request):

    perfil = obtener_perfil(request.user)

    if perfil.rol != PerfilUsuario.Roles.ADMIN:
        raise PermissionDenied(
            "No tienes permisos para realizar esta acción."
        )

    return perfil


# ==========================================
# INICIO - CONTROL DE PENDIENTES
# ==========================================

@login_required
def inicio(request):

    perfil = obtener_perfil(request.user)

    es_admin = perfil.rol == PerfilUsuario.Roles.ADMIN

    if es_admin:

        incidencias = Incidencia.objects.select_related(
            "sucursal",
            "creado_por",
            "responsable"
        ).all()

    else:

        if perfil.sucursal is None:
            raise PermissionDenied(
                "Tu usuario no tiene una sucursal asignada."
            )

        incidencias = Incidencia.objects.filter(
            sucursal=perfil.sucursal
        ).select_related(
            "sucursal",
            "creado_por",
            "responsable"
        )

    return render(
        request,
        "incidencias/inicio.html",
        {
            "incidencias": incidencias,
            "perfil": perfil,
        }
    )


# ==========================================
# NUEVA INCIDENCIA
# ==========================================

@login_required
def nueva_incidencia(request):

    perfil = obtener_perfil(request.user)

    es_admin = perfil.rol == PerfilUsuario.Roles.ADMIN

    if not es_admin and perfil.sucursal is None:
        raise PermissionDenied(
            "Tu usuario no tiene una sucursal asignada."
        )

    if request.method == "POST":

        formulario = IncidenciaForm(
            request.POST,
            es_admin=es_admin
        )

        if formulario.is_valid():

            incidencia = formulario.save(commit=False)

            incidencia.creado_por = request.user

            if not es_admin:
                incidencia.sucursal = perfil.sucursal

            incidencia.save()

            messages.success(
                request,
                "La incidencia se registró correctamente."
            )

            return redirect("inicio")

    else:

        formulario = IncidenciaForm(
            es_admin=es_admin
        )

    return render(
        request,
        "incidencias/nueva_incidencia.html",
        {
            "formulario": formulario,
            "perfil": perfil,
        }
    )


# ==========================================
# ADMINISTRAR TODAS LAS INCIDENCIAS
# ==========================================

@login_required
def administrar_incidencias(request):

    perfil = verificar_administrador(request)

    incidencias = Incidencia.objects.select_related(
        "sucursal",
        "creado_por",
        "responsable",
        "resuelto_por"
    ).all()

    return render(
        request,
        "incidencias/administrar_incidencias.html",
        {
            "incidencias": incidencias,
            "perfil": perfil,
        }
    )


# ==========================================
# EDITAR INCIDENCIA
# ==========================================

@login_required
def editar_incidencia(request, pk):

    verificar_administrador(request)

    incidencia = get_object_or_404(
        Incidencia,
        pk=pk
    )

    estado_anterior = incidencia.estado

    if request.method == "POST":

        formulario = AdministrarIncidenciaForm(
            request.POST,
            instance=incidencia
        )

        if formulario.is_valid():

            incidencia = formulario.save(commit=False)

            if incidencia.estado in [
                Incidencia.Estados.RESUELTA,
                Incidencia.Estados.CERRADA
            ]:

                if not incidencia.resuelto_en:
                    incidencia.resuelto_en = timezone.now()
                    incidencia.resuelto_por = request.user

            else:

                incidencia.resuelto_en = None
                incidencia.resuelto_por = None

            incidencia.save()

            if estado_anterior != incidencia.estado:

                Seguimiento.objects.create(
                    incidencia=incidencia,
                    usuario=request.user,
                    estado_anterior=estado_anterior,
                    estado_nuevo=incidencia.estado,
                    comentario=(
                        "Estado actualizado desde la "
                        "administración de incidencias."
                    )
                )

            messages.success(
                request,
                f"La incidencia {incidencia.folio} se actualizó correctamente."
            )

            return redirect("administrar_incidencias")

    else:

        formulario = AdministrarIncidenciaForm(
            instance=incidencia
        )

    return render(
        request,
        "incidencias/editar_incidencia.html",
        {
            "formulario": formulario,
            "incidencia": incidencia,
        }
    )


# ==========================================
# FINALIZAR INCIDENCIA
# ==========================================

@login_required
def finalizar_incidencia(request, pk):

    verificar_administrador(request)

    incidencia = get_object_or_404(
        Incidencia,
        pk=pk
    )

    if request.method != "POST":
        raise PermissionDenied(
            "La finalización debe realizarse mediante el formulario de confirmación."
        )

    if incidencia.estado in [
        Incidencia.Estados.RESUELTA,
        Incidencia.Estados.CERRADA
    ]:

        messages.warning(
            request,
            "Esta incidencia ya está finalizada."
        )

        return redirect("administrar_incidencias")

    estado_anterior = incidencia.estado

    incidencia.estado = Incidencia.Estados.CERRADA
    incidencia.resuelto_en = timezone.now()
    incidencia.resuelto_por = request.user

    if not incidencia.solucion:
        incidencia.solucion = (
            "Incidencia marcada como finalizada por Administración de Sistemas."
        )

    incidencia.save()

    Seguimiento.objects.create(
        incidencia=incidencia,
        usuario=request.user,
        estado_anterior=estado_anterior,
        estado_nuevo=Incidencia.Estados.CERRADA,
        comentario="Incidencia finalizada por Administración de Sistemas."
    )

    messages.success(
        request,
        f"La incidencia {incidencia.folio} fue finalizada correctamente."
    )

    return redirect("administrar_incidencias")


# ==========================================
# ELIMINAR INCIDENCIA
# ==========================================

@login_required
def eliminar_incidencia(request, pk):

    verificar_administrador(request)

    incidencia = get_object_or_404(
        Incidencia,
        pk=pk
    )

    if request.method == "POST":

        folio = incidencia.folio

        incidencia.delete()

        messages.success(
            request,
            f"La incidencia {folio} fue eliminada correctamente."
        )

        return redirect("administrar_incidencias")

    return render(
        request,
        "incidencias/eliminar_incidencia.html",
        {
            "incidencia": incidencia,
        }
    )


# ==========================================
# EXPORTAR PENDIENTES A EXCEL
# ==========================================

@login_required
def exportar_excel(request):

    perfil = obtener_perfil(request.user)

    es_admin = perfil.rol == PerfilUsuario.Roles.ADMIN

    if es_admin:

        incidencias = Incidencia.objects.select_related(
            "sucursal",
            "creado_por",
            "responsable"
        ).all()

    else:

        if perfil.sucursal is None:
            raise PermissionDenied(
                "Tu usuario no tiene una sucursal asignada."
            )

        incidencias = Incidencia.objects.filter(
            sucursal=perfil.sucursal
        ).select_related(
            "sucursal",
            "creado_por",
            "responsable"
        )

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Pendientes"

    encabezados = [
        "Folio",
        "Sucursal",
        "Tipo",
        "Categoría",
        "Título",
        "Descripción",
        "Prioridad",
        "Estado",
        "Reportado a",
        "Creado por",
        "Responsable",
        "Fecha de registro",
        "Solución",
    ]

    hoja.append(encabezados)

    for celda in hoja[1]:

        celda.font = Font(
            bold=True,
            color="FFFFFF"
        )

        celda.fill = PatternFill(
            start_color="1F4E78",
            end_color="1F4E78",
            fill_type="solid"
        )

        celda.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    for incidencia in incidencias:

        hoja.append([
            incidencia.folio,
            str(incidencia.sucursal),
            incidencia.get_tipo_display(),
            incidencia.categoria,
            incidencia.titulo,
            incidencia.descripcion,
            incidencia.get_prioridad_display(),
            incidencia.get_estado_display(),
            incidencia.reportado_a,
            incidencia.creado_por.username,
            incidencia.responsable.username if incidencia.responsable else "",
            incidencia.creado_en.strftime("%d/%m/%Y %H:%M"),
            incidencia.solucion,
        ])

    anchos = {
        "A": 18,
        "B": 25,
        "C": 20,
        "D": 22,
        "E": 35,
        "F": 50,
        "G": 15,
        "H": 18,
        "I": 25,
        "J": 20,
        "K": 20,
        "L": 22,
        "M": 50,
    }

    for columna, ancho in anchos.items():
        hoja.column_dimensions[columna].width = ancho

    hoja.freeze_panes = "A2"
    hoja.auto_filter.ref = hoja.dimensions

    respuesta = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    respuesta["Content-Disposition"] = (
        'attachment; filename="Control_de_Pendientes.xlsx"'
    )

    libro.save(respuesta)

    return respuesta
