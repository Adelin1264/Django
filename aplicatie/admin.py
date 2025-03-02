from django.contrib import admin
from .models import BluRay, Film, Director, Actor, Caracter, Gen

class FilmInline(admin.TabularInline):
    model = Film

class BluRayAdmin(admin.ModelAdmin):
    list_display = ('titlu', 'id', 'calitate_video', 'pret', 'stoc', 'subtitrari')
    search_fields = ('titlu',)
    list_per_page = 10
    
class GenAdmin(admin.ModelAdmin):
    list_display = ('denumire_gen', 'id', 'descriere_gen')
    search_fields = ('denumire_gen',)
    list_per_page = 10
    
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('nume_director', 'id', 'nationalitate_director', 'experienta', 'varsta_director')
    search_fields = ('nume_director',)
    list_per_page = 10
    inlines = [FilmInline]
    
class FilmAdmin(admin.ModelAdmin):
    list_display = ('nume_film', 'id')
    list_filter = ('gen', 'pt_adulti', 'data_lansare')
    search_fields = ('nume_film',)
    fieldsets = (
        ('Prezentare film', {
            'fields': ('nume_film', 'durata_film')
        }),
        ('Informatii generale', {
            'fields': ('descriere_film', 'data_lansare', 'pt_adulti')
        }),
        ('Informatii suplimentare', {
            'fields': ('gen', 'bluray', 'director'),
            'classes': ('collapse',),
        }),
    )
    list_per_page = 10
    
class ActorAdmin(admin.ModelAdmin):
    list_display = ('nume_actor', 'id', 'varsta_actor', 'nationalitate')
    search_fields = ('nume_actor',)
    list_per_page = 10
    
class CaracterAdmin(admin.ModelAdmin):
    list_display = ('nume_caracter', 'id', 'rol')
    list_filter = ('actor', 'rol')
    search_fields = ('nume_caracter',)
    fieldsets = (
        ('Informatii generale', {
            'fields': ('nume_caracter', 'rol')
        }),
        ('Informatii suplimentare', {
            'fields': ('film', 'actor'),
            'classes': ('collapse',),
        })
    )
    list_per_page = 10

admin.site.register(BluRay, BluRayAdmin)
admin.site.register(Film, FilmAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Caracter, CaracterAdmin)
admin.site.register(Actor, ActorAdmin)
admin.site.register(Gen, GenAdmin)

admin.site.index_title = "Panou Administrativ Filme"
admin.site.site_header = "Administrare Filme"

