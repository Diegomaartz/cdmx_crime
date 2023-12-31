from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

class crimeData(models.Model):
  user_report = models.CharField(default='Fiscalía General de Justicia (FGJ) de la Ciudad de México',max_length=200)
  delito = models.CharField(default='DELITO-No-especificado',max_length=255)
  categoria = models.CharField(default='CATEGORIA-No-especificada',max_length=100)
  anio_hecho = models.CharField(default='AÑO-No-especificado',max_length=100)
  fecha_hecho = models.CharField(default='FECHA-No-especificada',max_length=100)
  hora_hecho = models.CharField(default='HORA-No-especificada',max_length=100)
  colonia_hecho = models.CharField(default='COLONIA-No-especificada',max_length=100)
  alcaldia_hecho = models.CharField(default='ALCALDIA-No-especificada',max_length=100)
  latitud = models.CharField(default='LATITUD-No-especificada',max_length=255)
  longitud = models.CharField(default='LONGITUD-No-especificada',max_length=255)
  direccion = models.CharField(default='DIRECCION-No-especificada',max_length=500)
  

  def __str__(self):
        return f'{self.delito} - {self.categoria} - {self.alcaldia_hecho} - {self.anio_hecho} - {self.hora_hecho} - {self.colonia_hecho} - {self.latitud} - {self.longitud}'
  
  # class Meta:
  #     db_table = 'victimasfgj_2023_new'