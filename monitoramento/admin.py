from django.contrib import admin
from .models import *

admin.site.register(Usuario)
admin.site.register(Propriedade)
admin.site.register(Cultura)
admin.site.register(CulturaAgricola)
admin.site.register(UmidadeSolo)
admin.site.register(TemperaturaSolo)
admin.site.register(PhSolo)
admin.site.register(Recomendacao)
admin.site.register(Irrigacao)
admin.site.register(Notificacao)
@admin.register(Analise)
class AnaliseAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cultura", "score", "data_analise")
    list_filter = ("cultura", "classificacao")
@admin.register(ScoreAgronomico)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ("analise", "valor", "data")