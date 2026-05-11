from django.db import models


class Analise(models.Model):

    cultura = models.CharField(
        max_length=100
    )

    umidade = models.FloatField()

    ph = models.FloatField()

    temperatura = models.FloatField()

    recomendacao = models.TextField()

    def __str__(self):

        return self.cultura