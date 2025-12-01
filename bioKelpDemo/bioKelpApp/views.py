from django.shortcuts import render
from django.db.models import Sum
from bioKelpApp.models import Produccion, Stock
# Create your views here.

def renderTMetrica(request):
    # --- LOGICA DE PRODUCCION (La que ya tenías) ---
    resumen = Produccion.objects.values('tipo_alga').annotate(
        total_humeda=Sum('cantidad_humeda'),
        total_seca=Sum('cantidad_seca')
    )
    
    suma = 0
    for x in resumen:
        cant_h = x["total_humeda"] or 0
        cant_s = x["total_seca"] or 0
        suma += cant_h + cant_s

    # --- NUEVA LOGICA DE STOCK (Alertas) ---
    umbral_minimo = 1000  # Definimos el límite de 1000 kg
    
    # "cantidad_disponible__lt" significa "Less Than" (Menor que)
    alertas_stock = Stock.objects.filter(cantidad_disponible__lt=umbral_minimo)

    # --- CONTEXTO UNIFICADO ---
    contexto = {
        'suma': suma,
        'resumen_algas': resumen,
        # Agregamos las nuevas variables para usar en el HTML
        'alertas_stock': alertas_stock, 
        'umbral': umbral_minimo 
    }

    return render(request, 'templatesApp/metrica.html', contexto)

