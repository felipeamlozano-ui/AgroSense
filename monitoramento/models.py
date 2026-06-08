from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings

# =========================================================
# ANÁLISE RÁPIDA (USADA NO FORMULÁRIO DIRETO)
# =========================================================
class Analise(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analises_solos', null=True, blank=True)
    cultura = models.CharField(max_length=100)
    umidade = models.FloatField()
    ph = models.FloatField()
    temperatura = models.FloatField()
    recomendacao = models.TextField()

    def __str__(self):
        return self.cultura

    # ADICIONADO: Método para ajudar os gráficos do Dashboard a colorirem alertas
    @property
    def status_critico(self):
        """ Retorna se a análise apresenta índices perigosos para os gráficos """
        if self.ph < 5.5 or self.ph > 7.5 or self.umidade < 30 or self.temperatura > 35:
            return True
        return False


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
# PRODUTOR
# =========================================================

from django.conf import settings

class Produtor(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="produtores"
    )

    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nome


# =========================================================
# PROPRIEDADE RURAL
# =========================================================
class Propriedade(models.Model):
    produtor = models.ForeignKey(
        Produtor,
        on_delete=models.CASCADE,
        related_name='propriedades'
    )
    nome = models.CharField(max_length=150)
    localizacao = models.CharField(max_length=255)
    tamanho_hectares = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
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
# CULTURA AGRICOLA
# =========================================================
from django.db import models

class CulturaAgricola(models.Model):
    nome = models.CharField(max_length=120, unique=True)

    umidade_min = models.FloatField()
    umidade_max = models.FloatField()

    ph_min = models.FloatField()
    ph_max = models.FloatField()

    temperatura_min = models.FloatField()
    temperatura_max = models.FloatField()

    descricao = models.TextField(blank=True)

    fonte = models.CharField(
        max_length=50,
        default="EMBRAPA"
    )

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
    valor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    classificacao = models.CharField(
        max_length=10,
        choices=CLASSIFICACOES
    )
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
    valor = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    classificacao = models.CharField(
        max_length=10,
        choices=CLASSIFICACOES
    )
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
        validators=[
            MinValueValidator(0),
            MaxValueValidator(14)
        ]
    )
    classificacao = models.CharField(
        max_length=15,
        choices=CLASSIFICACOES
    )
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
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADES
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


# =========================================================
# ANÁLISE DO SOLO (COMPLETA / RELACIONAL)
# =========================================================
class AnaliseSolo(models.Model):
    cultura = models.ForeignKey(
        Cultura,
        on_delete=models.CASCADE,
        related_name='analises'
    )
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='analises'
    )
    umidade = models.ForeignKey(
        UmidadeSolo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ph = models.ForeignKey(
        PhSolo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    temperatura = models.ForeignKey(
        TemperaturaSolo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    recomendacao = models.ForeignKey(
        Recomendacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    observacoes = models.TextField(blank=True, null=True)
    data_analise = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Análise - {self.cultura.nome}"

    # ADICIONADO: Atalhos para a View de Relatórios e Gráficos acessar os valores sem quebrar
    @property
    def umidade_valor(self):
        return self.umidade.valor if self.umidade else 0

    @property
    def ph_valor(self):
        return self.ph.valor if self.ph else 0

    @property
    def temperatura_valor(self):
        return self.temperatura.valor if self.temperatura else 0


# =========================================================
# IRRIGAÇÃO
# =========================================================
class Irrigacao(models.Model):
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='irrigacoes'
    )
    quantidade_agua = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Quantidade em litros'
    )
    horario = models.DateTimeField()
    observacao = models.TextField(blank=True, null=True)
    automatica = models.BooleanField(default=False)

    def __str__(self):
        return f"Irrigação - {self.propriedade.nome}"


# =========================================================
# HISTÓRICO AGRÍCOLA
# =========================================================
class Historico(models.Model):
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='historicos'
    )
    descricao = models.TextField()
    data = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Histórico - {self.propriedade.nome}"


# =========================================================
# REGISTRO AGRÍCOLA
# =========================================================
class RegistroAgricola(models.Model):
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='registros'
    )
    descricao = models.TextField()
    data_registro = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Registro - {self.propriedade.nome}"


# =========================================================
# RELATÓRIOS
# =========================================================
class Relatorio(models.Model):
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='relatorios'
    )
    data_geracao = models.DateTimeField(auto_now_add=True)
    arquivo_pdf = models.FileField(
        upload_to='relatorios/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.titulo


# =========================================================
# NOTIFICAÇÕES (Mergulhado em uma única classe sem duplicidade)
# =========================================================
class Notificacao(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Usa o seu Usuario customizado de forma segura
        on_delete=models.CASCADE,
        related_name='notificacoes'
    )
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificação para {self.usuario}"