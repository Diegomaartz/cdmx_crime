from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import crimeData, Profile

from django.conf import settings

class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':' text-dark 	form-control ', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control text-dark', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control text-dark', 'placeholder':'Last Name'}))


	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-light"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-light small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-light"><small>Enter the same password as before, for verification.</small></span>'	

class AddReportForm(forms.ModelForm):
	user_report = forms.CharField(required=True,disabled=True, widget=forms.TextInput(attrs={"class": "form-control"}), label="Usuario:")
	delito = forms.CharField(required=True, widget=forms.TextInput(attrs={"placeholder": "Delito", "class": "form-control"}), label="Agrega una breve descripción del delito")
 
 
	categorias = [
		('DELITO DE BAJO IMPACTO', 'DELITO DE BAJO IMPACTO'),
		('ROBO A TRANSEUNTE EN VIA PUBLICA CON Y SIN VIOLENCIA', 'ROBO A TRANSEUNTE EN VIA PUBLICA CON Y SIN VIOLENCIA'),
		('ROBO DE VEHICULO CON Y SIN VIOLENCIA', 'ROBO DE VEHICULO CON Y SIN VIOLENCIA'),
		('HECHO NO DELICTIVO', 'HECHO NO DELICTIVO'),
		('LESIONES DOLOSAS POR DISPARO DE ARMA DE FUEGO', 'LESIONES DOLOSAS POR DISPARO DE ARMA DE FUEGO'),
		('VIOLACION', 'VIOLACION'),
		('ROBO A NEGOCIO CON VIOLENCIA', 'ROBO A NEGOCIO CON VIOLENCIA'),
		('ROBO A REPARTIDOR CON Y SIN VIOLENCIA', 'ROBO A REPARTIDOR CON Y SIN VIOLENCIA'),
		('HOMICIDIO DOLOSO', 'HOMICIDIO DOLOSO'),
		('ROBO A PASAJERO A BORDO DE MICROBUS CON Y SIN VIOLENCIA', 'ROBO A PASAJERO A BORDO DE MICROBUS CON Y SIN VIOLENCIA'),
		('ROBO A PASAJERO A BORDO DEL METRO CON Y SIN VIOLENCIA', 'ROBO A PASAJERO A BORDO DEL METRO CON Y SIN VIOLENCIA'),
		('ROBO A PASAJERO A BORDO DE TAXI CON VIOLENCIA', 'ROBO A PASAJERO A BORDO DE TAXI CON VIOLENCIA'),
		('ROBO A CUENTAHABIENTE SALIENDO DEL CAJERO CON VIOLENCIA', 'ROBO A CUENTAHABIENTE SALIENDO DEL CAJERO CON VIOLENCIA'),
		('ROBO A CASA HABITACIO CON VIOLENCIA', 'ROBO A CASA HABITACIO CON VIOLENCIA'),
	]
 
	categoria = forms.ChoiceField(choices=categorias,required=True, widget=forms.Select(attrs={ "class": "form-control"}), label="Categoría")
 
	fecha_hecho = forms.DateField(
        input_formats=['%d/%m/%Y'], 
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Fecha de hecho", "class": "form-control datepicker"}),
        label="Fecha de hecho DIA/MES/AÑO"
    )
	hora_hecho = forms.TimeField(required=True, widget=forms.TextInput(attrs={"placeholder": "Hora de hecho", "class": "form-control timepicker"}), label="Hora de hecho")
	colonia_hecho = forms.CharField(required=True, widget=forms.TextInput(attrs={"placeholder": "Colonia", "class": "form-control"}), label="Colonia")
 
	alcaldias = [
	('AZCAPOTZALCO', 'AZCAPOTZALCO'),
	('COYOACAN', 'COYOACAN'),
	('CUAJIMAPLA DE MORELOS', 'CUAJIMAPLA DE MORELOS'),
	('GUSTAVO A. MADERO', 'GUSTAVO A. MADERO'),
	('IZTACALCO', 'IZTACALCO'),
	('IZTAPALAPA', 'IZTAPALAPA'),
	('MAGDALENA CONTRERAS', 'MAGDALENA CONTRERAS'),
	('MILPA ALTA', 'MILPA ALTA'),
	('ALVARO OBREGON', 'ALVARO OBREGON'),
	('TLAHUAC', 'TLAHUAC'),
	('TLALPAN', 'TLALPAN'),
	('XOCHIMILCO', 'XOCHIMILCO'),
	('BENITO JUAREZ', 'BENITO JUAREZ'),
	('CUAUTHEMOC', 'CUAUTHEMOC'),
	('MIGUEL HIDALGO', 'MIGUEL HIDALGO'),
	('VENUSTIANO CARRANZA', 'VENUSTIANO CARRANZA'),
	]

	alcaldia_hecho = forms.ChoiceField(choices=alcaldias, required=True, widget=forms.Select(attrs={"class": "form-control"}), label="Alcaldía")
	direccion = forms.CharField(required=True, widget=forms.TextInput(attrs={"placeholder": "Dirección", "class": "form-control", "id": "direccion"}), label="Dirección")

	class Meta:
		model = crimeData
		exclude = ('anio_hecho', 'latitud', 'longitud')
