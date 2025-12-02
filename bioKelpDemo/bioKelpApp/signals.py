# bioKelpApp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lote, Movimiento

@receiver(post_save, sender=Lote)
def registrar_movimiento_por_lote(sender, instance, created, **kwargs):
    if created:
        if instance.cantidad_humedo_kg or instance.cantidad_seco_kg:
            Movimiento.objects.create(
                lote=instance,
                especie=instance.especie,
                tipo='produccion',
                cantidad_humedo_kg=instance.cantidad_humedo_kg,
                cantidad_seco_kg=instance.cantidad_seco_kg,
                descripcion=f'Lote creado {instance.codigo}'
            )
    else:
        Movimiento.objects.create(
            lote=instance,
            especie=instance.especie,
            tipo='etapa_update',
            descripcion=f'Actualización de etapas/fechas para lote {instance.codigo}'
        )
