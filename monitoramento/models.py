from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings

# =========================================================
# ANÁLISE RÁPIDA (USADA NO FORMULÁRIO DIRETO)
# =========================================================
class Analise(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cultura = models.ForeignKey("Cultura", on_delete=models.CASCADE)
    umidade = models.FloatField()
    ph = models.FloatField()
    temperatura = models.FloatField()
    recomendacao = models.ForeignKey("Recomendacao", on_delete=models.SET_NULL, null=True)
    score = models.IntegerField(default=0)
    classificacao = models.CharField(max_length=20, default="REGULAR")
    data_analise = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.cultura.nome

    @property
    def status_critico(self):
        return (
            self.ph < 5.5 or
            self.ph > 7.5 or
            self.umidade < 30 or
            self.temperatura > 35
        )

    @property
    def potencial_crescimento(self):
        return 0

# =========================================================
# USUÁRIO DO SISTEMA
# =========================================================
class Usuario(AbstractUser):
    nome_completo = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.nome_completo

# =========================================================
# PROPRIEDADE RURAL
# =========================================================
class Propriedade(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="propriedades"
    )
    nome = models.CharField(max_length=150)
    localizacao = models.CharField(max_length=255)
    tamanho_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    cultura_principal = models.CharField(max_length=100, blank=True, null=True)
    data_plantio = models.DateField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

# =========================================================
# CULTURA AGRÍCOLA
# =========================================================
class Cultura(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField()

    def __str__(self):
        return self.nome

# =========================================================
# CULTURA AGRICOLA (USADA PARA PARÂMETROS DA EMBRAPA)
# =========================================================
class CulturaAgricola(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    umidade_min = models.FloatField()
    umidade_max = models.FloatField()
    ph_min = models.FloatField()
    ph_max = models.FloatField()
    temperatura_min = models.FloatField()
    temperatura_max = models.FloatField()
    descricao = models.TextField(blank=True)
    fonte = models.CharField(max_length=50, default="EMBRAPA")
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

# =========================================================
# UMIDADE DO SOLO
# =========================================================
class UmidadeSolo(models.Model):
    CLASSIFICACOES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
    ]
    valor = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    classificacao = models.CharField(max_length=10, choices=CLASSIFICACOES)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.valor}% - {self.classificacao}"

# =========================================================
# TEMPERATURA DO SOLO
# =========================================================
class TemperaturaSolo(models.Model):
    CLASSIFICACOES = [
        ('FRIA', 'Fria'),
        ('IDEAL', 'Ideal'),
        ('QUENTE', 'Quente'),
    ]
    valor = models.DecimalField(max_digits=5, decimal_places=2)
    classificacao = models.CharField(max_length=10, choices=CLASSIFICACOES)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.valor}°C"

# =========================================================
# PH DO SOLO
# =========================================================
class PhSolo(models.Model):
    CLASSIFICACOES = [
        ('ACIDO', 'Ácido'),
        ('NEUTRO', 'Neutro'),
        ('ALCALINO', 'Alcalino'),
    ]
    valor = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(14)]
    )
    classificacao = models.CharField(max_length=15, choices=CLASSIFICACOES)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"pH {self.valor}"

# =========================================================
# RECOMENDAÇÕES AGRÍCOLAS
# =========================================================
class Recomendacao(models.Model):
    PRIORIDADES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    prioridade = models.CharField(max_length=10, choices=PRIORIDADES)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

# =========================================================
# IRRIGAÇÃO
# =========================================================
class Irrigacao(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='irrigacoes')
    cultura = models.CharField(max_length=100, blank=True, null=True)
    area_irrigada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantidade_agua = models.DecimalField(max_digits=10, decimal_places=2, help_text='Quantidade em litros')
    horario = models.DateTimeField()
    observacao = models.TextField(blank=True, null=True)
    automatica = models.BooleanField(default=False)
    eficiencia_hidrica = models.FloatField(default=0)

    def __str__(self):
        return f"Irrigação - {self.propriedade.nome}"

# =========================================================
# NOTIFICAÇÕES
# =========================================================
class Notificacao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificação para {self.usuario}"

# =========================================================
# SCORE AGRONÔMICO
# =========================================================
class ScoreAgronomico(models.Model):
    analise = models.ForeignKey(Analise, on_delete=models.CASCADE)
    valor = models.IntegerField()
    data = models.DateTimeField(auto_now_add=True)