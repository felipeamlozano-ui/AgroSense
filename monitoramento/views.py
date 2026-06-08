from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .ia.base_embrapa import EMBRAPA_DADOS
from .ia.gemini_service import gerar_relatorio_ia
from .forms import CustomLoginForm, CustomUserCreationForm
from .models import (
    Analise, Cultura, Propriedade, UmidadeSolo, TemperaturaSolo,
    PhSolo, Recomendacao, AnaliseSolo,
    Historico, Relatorio, Notificacao,
    Produtor, Irrigacao, RegistroAgricola
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

    if not request.user.is_authenticated:
        return redirect("/?erro=login")

    notificacoes = request.user.notificacoes.filter(lida=False).order_by("-data_envio")
    notificacoes_nao_lidas = notificacoes.count()

    erro = None

    if request.method == "POST":

        cultura_nome = (request.POST.get("cultura") or "desconhecida").strip().capitalize()

        umidade = safe_float(request.POST.get("umidade"))
        ph = safe_float(request.POST.get("ph"))
        temperatura = safe_float(request.POST.get("temperatura"))

        # =========================
        # 1. BUSCA CULTURA NO BANCO
        # =========================
        obj_cultura = CulturaAgricola.objects.filter(
            nome__iexact=cultura_nome
        ).first()

        # =========================
        # 2. FALLBACK EMBRAPA
        # =========================
        if obj_cultura:
            referencia = {
                "umidade_ideal": (obj_cultura.umidade_min, obj_cultura.umidade_max),
                "ph_ideal": (obj_cultura.ph_min, obj_cultura.ph_max),
                "temperatura_ideal": (obj_cultura.temperatura_min, obj_cultura.temperatura_max),
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

        # =========================
        # 3. DADOS DO SOLO
        # =========================
        dados_solo = {
            "umidade": umidade,
            "ph": ph,
            "temperatura": temperatura
        }

        # =========================
        # 4. IA GEMINI
        # =========================
        relatorio = gerar_relatorio_ia(
            cultura=cultura_nome,
            dados_solo=dados_solo,
            referencia_embrapa=referencia
        )

        # =========================
        # 5. SALVAR
        # =========================
        Analise.objects.create(
            usuario=request.user,
            cultura=cultura_nome,
            umidade=umidade,
            ph=ph,
            temperatura=temperatura,
            recomendacao=relatorio
        )

        # =========================
        # 6. NOTIFICAÇÃO
        # =========================
        Notificacao.objects.create(
            usuario=request.user,
            mensagem=f"Relatório IA gerado para {cultura_nome}",
            lida=False
        )

        messages.success(request, "Relatório inteligente gerado com sucesso!")
        return redirect("monitoramento")

    # =========================
    # GET (TELA)
    # =========================
    analises = Analise.objects.filter(usuario=request.user).order_by("-id")
    ultima_analise = analises.first()

    ph_porcentagem = (float(ultima_analise.ph) / 14.0) * 100 if ultima_analise else 0
    temp_porcentagem = (float(ultima_analise.temperatura) / 50.0) * 100 if ultima_analise else 0

    return render(request, "monitoramento/monitoramento.html", {
        "analises": analises,
        "ultima_analise": ultima_analise,
        "notificacoes": notificacoes,
        "notificacoes_nao_lidas": notificacoes_nao_lidas,
        "ph_porcentagem": ph_porcentagem,
        "temp_porcentagem": temp_porcentagem,
        "erro": erro
    })
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

    if request.method == "POST":
        tipo = request.POST.get("tipo")

        # PRODUTOR
        if tipo == "produtor":
            produtor = Produtor.objects.create(
                usuario=request.user,
                nome=request.POST.get("nome"),
                cpf=request.POST.get("cpf"),
                telefone=request.POST.get("telefone"),
                email=request.POST.get("email")
            )

            Notificacao.objects.create(
                usuario=request.user,
                mensagem=f"Novo produtor cadastrado: {produtor.nome}",
                lida=False
            )

        # PROPRIEDADE
        elif tipo == "propriedade":
            produtor = get_object_or_404(
                Produtor,
                id=request.POST.get("produtor"),
                usuario=request.user
            )

            propriedade = Propriedade.objects.create(
                produtor=produtor,
                nome=request.POST.get("nome"),
                localizacao=request.POST.get("localizacao"),
                tamanho_hectares=request.POST.get("hectares")
            )

            Notificacao.objects.create(
                usuario=request.user,
                mensagem=f"Nova propriedade cadastrada: {propriedade.nome}",
                lida=False
            )

        # IRRIGAÇÃO
        elif tipo == "irrigacao":
            propriedade = get_object_or_404(
                Propriedade,
                id=request.POST.get("propriedade"),
                produtor__usuario=request.user
            )

            irrigacao = Irrigacao.objects.create(
                propriedade=propriedade,
                quantidade_agua=request.POST.get("agua"),
                horario=request.POST.get("horario"),
                observacao=request.POST.get("observacao"),
                automatica="automatica" in request.POST
            )

            Notificacao.objects.create(
                usuario=request.user,
                mensagem=f"Irrigação registrada: {irrigacao.quantidade_agua}L",
                lida=False
            )

        # REGISTRO
        elif tipo == "registro":
            propriedade = get_object_or_404(
                Propriedade,
                id=request.POST.get("propriedade"),
                produtor__usuario=request.user
            )

            registro = RegistroAgricola.objects.create(
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

    return render(request, "monitoramento/gestao.html", {
        "produtores": Produtor.objects.filter(usuario=request.user),
        "propriedades": Propriedade.objects.filter(produtor__usuario=request.user),
        "irrigacoes": Irrigacao.objects.filter(propriedade__produtor__usuario=request.user).order_by("-id")[:10],
        "registros": RegistroAgricola.objects.filter(propriedade__produtor__usuario=request.user).order_by("-id")[:10],
    })