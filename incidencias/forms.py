from django import forms
from django.contrib.auth import get_user_model

from .models import Incidencia, Sucursal


Usuario = get_user_model()


# ==========================================
# FORMULARIO PARA REGISTRAR INCIDENCIAS
# ==========================================

class IncidenciaForm(forms.ModelForm):

    reportado_a = forms.CharField(
        required=False,
        label="Responsable al que se reportó",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nombre de la persona a quien se reportó",
            }
        ),
    )

    sucursal = forms.ModelChoiceField(
        queryset=Sucursal.objects.filter(activa=True),
        required=True,
        label="Sucursal",
        empty_label="Selecciona una sucursal",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    class Meta:
        model = Incidencia

        fields = [
            "sucursal",
            "tipo",
            "categoria",
            "titulo",
            "descripcion",
            "prioridad",
            "reportado_a",
        ]

        labels = {
            "sucursal": "Sucursal",
            "tipo": "Tipo de registro",
            "categoria": "Categoría",
            "titulo": "Título del reporte",
            "descripcion": "Descripción detallada",
            "prioridad": "Prioridad",
            "reportado_a": "Responsable al que se reportó",
        }

        widgets = {
            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "categoria": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "titulo": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),
            "prioridad": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        es_admin = kwargs.pop("es_admin", False)

        super().__init__(*args, **kwargs)

        # Forzar categoría como lista desplegable
        self.fields["categoria"].widget = forms.Select(
            attrs={
                "class": "form-select",
            }
        )

        # Los usuarios de sucursal no seleccionan la sucursal
        if not es_admin:
            self.fields.pop("sucursal")


# ==========================================
# FORMULARIO EXCLUSIVO PARA ADMINISTRADOR
# ==========================================

class AdministrarIncidenciaForm(forms.ModelForm):

    class Meta:
        model = Incidencia

        fields = [
            "sucursal",
            "tipo",
            "categoria",
            "titulo",
            "descripcion",
            "prioridad",
            "estado",
            "reportado_a",
            "responsable",
            "solucion",
        ]

        labels = {
            "sucursal": "Sucursal",
            "tipo": "Tipo de registro",
            "categoria": "Categoría",
            "titulo": "Título",
            "descripcion": "Descripción",
            "prioridad": "Prioridad",
            "estado": "Estado de la incidencia",
            "reportado_a": "Reportado a",
            "responsable": "Responsable de Sistemas",
            "solucion": "Solución o comentarios",
        }

        widgets = {
            "sucursal": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "categoria": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "titulo": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "prioridad": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "estado": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "reportado_a": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "responsable": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "solucion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe la solución aplicada...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["sucursal"].queryset = Sucursal.objects.filter(
            activa=True
        )

        self.fields["responsable"].queryset = Usuario.objects.filter(
            is_active=True
        )

        self.fields["responsable"].required = False
        self.fields["responsable"].empty_label = "Sin asignar"