from django.contrib import admin
from .models import Lote, Movimiento, Especie, Planta, Alerta

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'especie',
        'origen',
        'fecha_cosecha',
        'fecha_almacenamiento',
        'fecha_procesamiento',
        'creado_en',
    )
    list_filter = ('especie', 'origen')
    search_fields = ('codigo', 'especie__nombre', 'origen__nombre')


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'lote',
        'especie',
        'tipo',
        'cantidad_humedo_kg',
        'cantidad_seco_kg',
        'fecha',
        'usuario',
    )
    list_filter = ('tipo', 'especie')
    search_fields = ('lote__codigo', 'especie__nombre', 'descripcion')


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Planta)
class PlantaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('id', 'especie', 'nivel', 'mensaje', 'creada_en', 'leida')
    list_filter = ('nivel', 'especie')
    search_fields = ('mensaje', 'especie__nombre')
    