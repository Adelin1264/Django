from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.conf import settings

class BluRay(models.Model):
    titlu = models.CharField(max_length=50)
    calitate_video = models.CharField(max_length=10)
    pret = models.DecimalField(max_digits=5, decimal_places=2)
    stoc = models.PositiveIntegerField()
    subtitrari = models.BooleanField(default=True)
    imagine = models.ImageField(upload_to='blurays/', null=True, blank=True)

class Gen(models.Model):
    denumire_gen = models.CharField(max_length=30)
    descriere_gen = models.TextField(max_length=300, blank=True, null=True)

class Director(models.Model):
    nume_director = models.CharField(max_length=30)
    nationalitate_director = models.CharField(max_length=30)
    experienta = models.PositiveIntegerField()
    varsta_director = models.PositiveIntegerField()

class Film(models.Model):
    nume_film = models.CharField(max_length=50)
    descriere_film = models.TextField(max_length=300, blank=True , null=True)
    durata_film = models.DurationField()
    data_lansare = models.DateField()
    pt_adulti = models.BooleanField(default=False)
    bluray = models.ManyToManyField(BluRay, related_name='filme')
    gen = models.ManyToManyField(Gen)
    director = models.ForeignKey(Director, on_delete=models.CASCADE)

class Actor(models.Model):
    nume_actor = models.CharField(max_length=30)
    varsta_actor = models.PositiveIntegerField()
    nationalitate = models.CharField(max_length=30)
    
class Caracter(models.Model):
    Roluri = [('PROTAGONIST', 'Protagonist'),
        ('ANTAGONIST', 'Antagonist'),
        ('SECUNDAR', 'Secundar')]
    nume_caracter = models.CharField(max_length=30)
    rol = models.CharField(choices=Roluri)
    film = models.ManyToManyField(Film)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    
    
class CustomUser(AbstractUser):
    telefon = models.CharField(max_length=15, blank=True, null=True)
    adresa = models.TextField(blank=True, null=True)
    data_nasterii = models.DateField(blank=True, null=True)
    ocupatie = models.CharField(max_length=100, blank=True, null=True)
    descriere_personala = models.TextField(blank=True, null=True)
    cod = models.CharField(max_length=100, blank=True, null=True)
    email_confirmat = models.BooleanField(default=False)
    
class Vizualizare(models.Model):
    utilizator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bluray = models.ForeignKey(BluRay, on_delete=models.CASCADE)
    data_vizualizarii = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_vizualizarii']
        
class Promotie(models.Model):
    nume = models.CharField(max_length=100)
    data_creare = models.DateTimeField(auto_now_add=True)
    data_expirare = models.DateTimeField()
    reducere = models.DecimalField(max_digits=5, decimal_places=2)
    calitate_video = models.CharField(max_length=10, blank=True, null=True)
    subtitrari = models.BooleanField(default=True)

    def __str__(self):
        return self.nume