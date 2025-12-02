from django import forms
from .models import Cliente, Lote, Movimiento, Especie, Planta



# Lista de opciones para el Select de Países (puedes agregar más)
PAISES_CHOICES = [
    ('', 'Seleccione un país'),
    ('Chile', 'Chile'),
    ('Argentina', 'Argentina'),
    ('Perú', 'Perú'),
    ('Bolivia', 'Bolivia'),
    ('Brasil', 'Brasil'),
    ('Colombia', 'Colombia'),
    ('Ecuador', 'Ecuador'),
    ('Venezuela', 'Venezuela'),
    ('Uruguay', 'Uruguay'),
    ('Paraguay', 'Paraguay'),
    ('México', 'México'),
    ('Estados Unidos', 'Estados Unidos'),
    ('España', 'España'),
    # Agrega el resto de tu lista aquí...
]

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__' # Usamos todos los campos del modelo

        # Aquí "disfrazamos" los inputs de Django para que tengan tu diseño
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'input-group', 
                'placeholder': 'Ingrese el nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'input-group', 
                'placeholder': 'Ingrese el apellido'
            }),
            'rut': forms.TextInput(attrs={
                'class': 'input-group', 
                'placeholder': 'Ej: 12.345.678-9'
            }),
            'pais': forms.Select(choices=PAISES_CHOICES, attrs={
                'class': 'input-group',
                'id': 'pais'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'input-group', 
                'placeholder': 'ejemplo@correo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'input-group', 
                'placeholder': '+56 9 1234 5678'
            }),
        }

    # Validación extra: Verificar si el RUT ya existe
    def clean_rut(self):
            rut = self.cleaned_data.get('rut')

            # 1. Limpieza básica: Quitamos puntos y guiones para quedarnos solo con números y K
            rut_limpio = rut.replace(".", "").replace("-", "").upper()

            # 2. Verificar formato: Debe tener al menos 8 caracteres (7 números + 1 DV)
            if len(rut_limpio) < 8:
                raise forms.ValidationError("El RUT es demasiado corto.")

            # Separamos el cuerpo del dígito verificador
            cuerpo = rut_limpio[:-1]
            dv_ingresado = rut_limpio[-1]

            # 3. Validar que el cuerpo sean solo números
            if not cuerpo.isdigit():
                raise forms.ValidationError("El cuerpo del RUT debe contener solo números.")

            # --- ALGORITMO MÓDULO 11 (Matemática Chilena) ---
            suma = 0
            multiplo = 2

            # Recorremos los números al revés
            for c in reversed(cuerpo):
                suma += int(c) * multiplo
                multiplo += 1
                if multiplo > 7:
                    multiplo = 2
            
            # Calculamos el dígito esperado
            dvr = 11 - (suma % 11)
            
            if dvr == 11:
                dv_calculado = '0'
            elif dvr == 10:
                dv_calculado = 'K'
            else:
                dv_calculado = str(dvr)

            # 4. Comparación final
            if dv_calculado != dv_ingresado:
                raise forms.ValidationError("El RUT ingresado no es válido (Dígito verificador incorrecto).")

            # 5. Verificamos duplicados (lo que ya tenías)
            # Excluimos al propio cliente si se estuviera editando (opcional, pero buena práctica)
            if Cliente.objects.filter(rut=rut).exists():
                raise forms.ValidationError("Este RUT ya está registrado en el sistema.")

            return rut
    



class LoteForm(forms.ModelForm):
    # Campos de texto que verá el usuario
    especie_nombre = forms.CharField(
        label="Especie",
        max_length=120,
        required=True,
    )
    origen_nombre = forms.CharField(
        label="Origen / Planta",
        max_length=120,
        required=True,
    )

    class Meta:
        model = Lote
        fields = [
            'codigo',
            'cantidad_humedo_kg',
            'cantidad_seco_kg',
            'fecha_cosecha',
            'fecha_almacenamiento',
            'fecha_procesamiento',
        ]
        widgets = {
            'fecha_cosecha': forms.DateInput(attrs={'type': 'date'}),
            'fecha_almacenamiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_procesamiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cuando editas un lote existente, rellenar los campos de texto
        if self.instance and self.instance.pk:
            if self.instance.especie:
                self.fields['especie_nombre'].initial = self.instance.especie.nombre
            if self.instance.origen:
                self.fields['origen_nombre'].initial = self.instance.origen.nombre

    def clean(self):
        cleaned = super().clean()
        fc = cleaned.get('fecha_cosecha')
        fa = cleaned.get('fecha_almacenamiento')
        fp = cleaned.get('fecha_procesamiento')

        if fa and fc and fa < fc:
            self.add_error('fecha_almacenamiento', 'La fecha de almacenamiento no puede ser anterior a la fecha de cosecha.')

        if fp and fa and fp < fa:
            self.add_error('fecha_procesamiento', 'La fecha de procesamiento no puede ser anterior a la fecha de almacenamiento.')

        return cleaned

    def save(self, commit=True):

        especie_nombre = self.cleaned_data.get('especie_nombre')
        origen_nombre = self.cleaned_data.get('origen_nombre')

        # Crear o recuperar Especie
        especie_obj, _ = Especie.objects.get_or_create(nombre=especie_nombre)

        # Crear o recuperar Planta (origen)
        origen_obj, _ = Planta.objects.get_or_create(nombre=origen_nombre)

        lote = super().save(commit=False)
        lote.especie = especie_obj
        lote.origen = origen_obj

        if commit:
            lote.save()

        return lote

class MovimientoForm(forms.ModelForm):
    especie_nombre = forms.CharField(
        label="Especie",
        max_length=120,
        required=True,
    )

    class Meta:
        model = Movimiento
        fields = [
            'lote',
            'tipo',
            'cantidad_humedo_kg',
            'cantidad_seco_kg',
            'descripcion',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.especie:
            self.fields['especie_nombre'].initial = self.instance.especie.nombre

    def save(self, commit=True):
        especie_nombre = self.cleaned_data.get('especie_nombre')
        especie_obj, _ = Especie.objects.get_or_create(nombre=especie_nombre)

        mov = super().save(commit=False)
        mov.especie = especie_obj

        if commit:
            mov.save()

        return mov
