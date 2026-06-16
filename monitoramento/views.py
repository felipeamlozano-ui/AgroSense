from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from .models import ScoreAgronomico
import json
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from .ia.service import gerar_relatorio_ia
from .forms import CustomLoginForm, CustomUserCreationForm
from .models import (
    Analise, Cultura, Propriedade, UmidadeSolo, TemperaturaSolo,
    PhSolo, Recomendacao, Notificacao,
    Usuario, Irrigacao,
)

Usuario = get_user_model()


# =========================================================
# LOGIN / CADASTRO
# =========================================================
class UsuarioLoginView(LoginView):
    template_name = 'monitoramento/login.html'
    authentication_form = CustomLoginForm

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        if action == "login":
            form = self.get_form()
            if form.is_valid():
                login(request, form.get_user())
                return redirect("index")
            messages.error(request, "Usuário ou senha inválidos.")
            return self.form_invalid(form)

        elif action == "register":
            email = request.POST.get("username")
            password = request.POST.get("password")

            if Usuario.objects.filter(email=email).exists():
                messages.error(request, "Já existe um usuário com esse email.")
                return redirect("login")

            Usuario.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            messages.success(request, "Usuário criado com sucesso!")
            return redirect("login")

        return super().post(request, *args, **kwargs)


def cadastro(request):
    form = CustomUserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Conta criada com sucesso!")
        return redirect("login")

    return render(request, "monitoramento/cadastro.html", {"form": form})


# =========================================================
# INDEX
# =========================================================
def index(request):
    analises = Analise.objects.filter(usuario=request.user).order_by("-id") if request.user.is_authenticated else []
    return render(request, "monitoramento/index.html", {"analises": analises})


# =========================================================
# CADASTRAR ANALISE
# =========================================================
def cadastrar(request):
    if not request.user.is_authenticated:
        return redirect("/?erro=login")

    if request.method == "POST":
        try:
            Analise.objects.create(
                usuario=request.user,
                cultura=request.POST.get("cultura", "Milho"),
                umidade=float(str(request.POST.get("umidade", 0)).replace(",", ".")),
                ph=float(str(request.POST.get("ph", 0)).replace(",", ".")),
                temperatura=float(str(request.POST.get("temperatura", 0)).replace(",", ".")),
                recomendacao="Análise gerada automaticamente"
            )
        except Exception as e:
            print("Erro:", e)

        return redirect("index")

    return render(request, "monitoramento/cadastrar.html")


# =========================================================
# MONITORAMENTO
# =========================================================
from .models import CulturaAgricola

def safe_float(value, default=0.0):
    try:
        return float(str(value).replace(",", "."))
    except:
        return default


@login_required
def monitoramento(request):

    notificacoes = request.user.notificacoes.filter(
        lida=False
    ).order_by("-data_envio")

    notificacoes_nao_lidas = notificacoes.count()

    erro = None

    if request.method == "POST":

        cultura_nome = (
            request.POST.get("cultura")
            or "desconhecida"
        ).strip().capitalize()

        umidade = UmidadeSolo.objects.last().valor
        ph = safe_float(request.POST.get("ph"))
        temperatura = safe_float(request.POST.get("temperatura"))

        obj_cultura = CulturaAgricola.objects.filter(
            nome__iexact=cultura_nome
        ).first()

        if obj_cultura:
            referencia = {
                "umidade_ideal": (
                    obj_cultura.umidade_min,
                    obj_cultura.umidade_max
                ),
                "ph_ideal": (
                    obj_cultura.ph_min,
                    obj_cultura.ph_max
                ),
                "temperatura_ideal": (
                    obj_cultura.temperatura_min,
                    obj_cultura.temperatura_max
                ),
                "descricao": obj_cultura.descricao,
                "fonte": obj_cultura.fonte
            }
        else:
            referencia = {
                "umidade_ideal": (40, 60),
                "ph_ideal": (5.5, 6.5),
                "temperatura_ideal": (20, 30),
                "descricao": "Cultura sem base cadastrada no sistema.",
                "fonte": "Sistema padrão"
            }

        dados_solo = {
            "umidade": umidade,
            "ph": ph,
            "temperatura": temperatura
        }

        relatorio = gerar_relatorio_ia(
            cultura=cultura_nome,
            dados_solo=dados_solo,
            referencia_embrapa=referencia
        )

        # 1. Cultura
        cultura_obj, _ = Cultura.objects.get_or_create(
            nome=cultura_nome,
            defaults={"descricao": ""}
        )

        # 2. Sensores
        umidade_obj = UmidadeSolo.objects.create(
            valor=umidade,
            classificacao="MEDIA"
        )

        ph_obj = PhSolo.objects.create(
            valor=ph,
            classificacao="NEUTRO" if 5.5 <= ph <= 7.5 else "ACIDO"
        )

        temp_obj = TemperaturaSolo.objects.create(
            valor=temperatura,
            classificacao="IDEAL"
        ) 

        # 3. Recomendação
        recomendacao_obj = Recomendacao.objects.create(
            titulo=f"Relatório IA - {cultura_nome}",
            descricao=relatorio,
            prioridade="MEDIA"
        )

        # 4. Analise principal
        umidade = Decimal(request.POST.get('umidade'))
        ph = Decimal(request.POST.get('ph'))
        temperatura = Decimal(request.POST.get('temperatura'))

        analise = Analise.objects.create(
            usuario=request.user,
            cultura=cultura_obj,
            umidade=umidade,
            ph=ph,  # Aqui você salva o número direto, por isso no GET não se usa .valor
            temperatura=temperatura,
            recomendacao=recomendacao_obj,
            score=round((umidade + ph + temperatura) / Decimal("3")),
            classificacao="REGULAR"
        )

        # 5. Histórico de score
        ScoreAgronomico.objects.create(
            analise=analise,
            valor=analise.score
        )

        Notificacao.objects.create(
            usuario=request.user,
            mensagem=f"Relatório IA gerado para {cultura_nome}",
            lida=False
        )

        messages.success(
            request,
            "Relatório inteligente gerado com sucesso!"
        )

        return redirect("monitoramento")

    analises = Analise.objects.filter(
        usuario=request.user
    ).order_by("-id")

    ultima_analise = analises.first()

    ph_porcentagem = (
        (float(ultima_analise.ph) / 14.0) * 100
        if ultima_analise else 0
    )

    temp_porcentagem = (
        (float(ultima_analise.temperatura) / 50.0) * 100
        if ultima_analise else 0
    )

    return render(
        request,
        "monitoramento/monitoramento.html",
        {
            "analises": analises,
            "ultima_analise": ultima_analise,
            "notificacoes": notificacoes,
            "notificacoes_nao_lidas": notificacoes_nao_lidas,
            "ph_porcentagem": ph_porcentagem,
            "temp_porcentagem": temp_porcentagem,
            "erro": erro
        }
    )
# =========================================================
# NOTIFICAÇÕES
# =========================================================
@login_required
def detalhe_notificacao(request, notificacao_id):
    notificacao = get_object_or_404(
        Notificacao,
        id=notificacao_id,
        usuario=request.user
    )
    notificacao.lida = True
    notificacao.save()

    return render(request, "monitoramento/notificacao.html", {"notificacao": notificacao})


@login_required
def marcar_todas_lidas(request):
    Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
    return redirect(request.META.get("HTTP_REFERER", "/"))


# =========================================================
# GESTÃO AGRÍCOLA (CORRIGIDA)
# =========================================================
@login_required
def gestao_agricola(request):

    # =========================
    # POST (cadastros)
    # =========================
    if request.method == "POST":
        tipo = request.POST.get("tipo")

        # -----------------
        # PROPRIEDADE
        # -----------------
        if tipo == "propriedade":
            propriedade = Propriedade.objects.create(
                usuario=request.user,
                nome=request.POST.get("nome"),
                localizacao=request.POST.get("localizacao"),
                tamanho_hectares=request.POST.get("hectares"),
                cultura_principal=request.POST.get("cultura"),
                data_plantio=request.POST.get("data_plantio") or None
            )

            Notificacao.objects.create(
                usuario=request.user,
                mensagem=f"Nova propriedade cadastrada: {propriedade.nome}",
                lida=False
            )

        # -----------------
        # IRRIGAÇÃO
        # -----------------
        elif tipo == "irrigacao":
            propriedade = get_object_or_404(
                Propriedade,
                id=request.POST.get("propriedade"),
                usuario=request.user
            )

            Irrigacao.objects.create(
                propriedade=propriedade,
                cultura=request.POST.get("cultura"),
                area_irrigada=request.POST.get("area"),
                quantidade_agua=request.POST.get("agua"),
                horario=request.POST.get("horario"),
                observacao=request.POST.get("observacao"),
                automatica="automatica" in request.POST
            )

            Notificacao.objects.create(
                usuario=request.user,
                mensagem=f"Irrigação registrada com sucesso",
                lida=False
            )

        # -----------------
        # REGISTRO AGRÍCOLA
        # -----------------
        elif tipo == "registro":
            propriedade = get_object_or_404(
                Propriedade,
                id=request.POST.get("propriedade"),
                usuario=request.user
            )

            RegistroAgricola.objects.create(
                propriedade=propriedade,
                descricao=request.POST.get("descricao")
            )

            Notificacao.objects.create(
                usuario=request.user,
                mensagem=f"Registro agrícola criado em {propriedade.nome}",
                lida=False
            )

        messages.success(request, "Registro salvo com sucesso!")
        return redirect("gestao_agricola")

    # =========================
    # GET (dashboard)
    # =========================

    propriedades = Propriedade.objects.filter(
        usuario=request.user
    )

    irrigacoes = Irrigacao.objects.filter(
        propriedade__usuario=request.user
    ).order_by("-id")[:10]

    analises = Analise.objects.filter(
        usuario=request.user
    ).order_by("-id")

    total_analises = analises.count()

    score_medio = (
        sum(a.score for a in analises) / analises.count()
        if analises.exists() else 0
    )

    alertas_criticos = sum(
        1 for a in analises
            if a.ph < 5.5 or a.ph > 7.5
    )

    ultimas_analises = analises.order_by("-data_analise")[:10]
    # =========================
    # GRÁFICO ANÁLISES
    # =========================
    grafico_datas = [
    a.data_analise.strftime("%d/%m")
        for a in reversed(ultimas_analises)
    ]

    grafico_potencial = [
        float(a.ph or 0)
        for a in reversed(ultimas_analises)
    ]
    score_dados = [
    {
        "data": a.data_analise.strftime("%d/%m") if a.data_analise else "",
        "score": float(score_medio or 0)  # substitui depois se tiver score real
    }
    for a in reversed(analises.order_by("-data_analise")[:10])
    ]

    # =========================
    # GRÁFICO IRRIGAÇÃO
    # =========================
    agua_labels = [
        i.horario.strftime("%d/%m")
        for i in reversed(irrigacoes)
    ]

    agua_dados = [
        float(i.quantidade_agua)
        for i in reversed(irrigacoes)
    ]

    # =========================
    # RECOMENDAÇÕES (CORRIGIDO)
    # =========================
    recomendacoes = [
        a.recomendacao
        for a in analises
        if a.recomendacao
    ][:5]

    return render(
    request,
    "monitoramento/gestao.html",
    {
        "propriedades": propriedades,
        "irrigacoes": irrigacoes,

        "analises": analises,
        "total_analises": total_analises,
        "score_medio": round(score_medio, 2),
        "alertas_criticos": alertas_criticos,

        "ultima_analise": ultimas_analises.first(),
        "ultimas_analises": analises[:10],

        "grafico_datas": json.dumps(grafico_datas),
        "grafico_potencial": json.dumps(grafico_potencial),
        "grafico_score": json.dumps({
            "chartType": "line",
            "meta": {
                "title": "Evolução do Score",
                "description": "Variação do score das análises ao longo do tempo."
            },
            "xKey": "data",
            "xAxisLabel": "Data",
            "series": [
            {
                "dataKey": "score",
                "label": "Score",
                "valueFormat": "integer"
            }
        ],
            "data": score_dados
        }),
        "agua_labels": json.dumps(agua_labels),
        "agua_dados": json.dumps(agua_dados),

        "recomendacoes": recomendacoes,

        "notificacoes": request.user.notificacoes.filter(lida=False),
        "notificacoes_nao_lidas": request.user.notificacoes.filter(lida=False).count(),
    }
)