from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.utils import timezone  # <-- ESSA LINHA RESOLVE O ERRO

from .forms import CustomLoginForm, CustomUserCreationForm
from .models import (
    Analise, Cultura, Propriedade, UmidadeSolo, TemperaturaSolo, 
    PhSolo, Recomendacao, AnaliseSolo,
    Historico, Relatorio, Notificacao
)

# Definição do modelo customizado de Usuário do AgroSense
Usuario = get_user_model()

# =========================================================
# AUTENTICAÇÃO (LOGIN / CADASTRO)
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
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faça seu login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'monitoramento/cadastro.html', {'form': form})


# =========================================================
# HOME / INDEX
# =========================================================
def index(request):
    # Captura o parâmetro de erro de redirecionamento do monitoramento
    if request.GET.get('erro') == 'login':
        messages.warning(request, 'Você precisa estar logado para acessar a página de Monitoramento!')

    try:
        # Se estiver logado, mostra apenas as dele. Se não estiver, lista vazia.
        if request.user.is_authenticated:
            analises = Analise.objects.filter(usuario=request.user).order_by("-id")
        else:
            analises = []
        erro = None
    except Exception as e:
        analises = []
        erro = str(e)

    return render(
        request,
        "monitoramento/index.html",
        {"analises": analises, "erro": erro}
    )


def cadastrar(request):
    # Bloqueio de segurança manual para a rota de cadastro rápido de análise
    if not request.user.is_authenticated:
        return redirect('/?erro=login')

    if request.method == "POST":
        try:
            Analise.objects.create(
                usuario=request.user,  # Vincula ao usuário atual
                cultura=request.POST.get("cultura", "Milho"),
                umidade=float(str(request.POST.get("umidade", 0)).replace(',', '.')),
                ph=float(str(request.POST.get("ph", 0)).replace(',', '.')),
                temperatura=float(str(request.POST.get("temperatura", 0)).replace(',', '.')),
                recomendacao="Análise gerada automaticamente"
            )
        except Exception as e:
            print("🔥 ERRO AO SALVAR:", e)
        return redirect("index")

    return render(request, "monitoramento/cadastrar.html")


# =========================================================
# MONITORAMENTO AGROSENSE
# =========================================================
def monitoramento(request):
    if not request.user.is_authenticated:
        return redirect('/?erro=login')

    # CORREÇÃO: Definindo a variável para requisições GET não quebrarem o contexto
    erro = None 
    notificacoes_nao_lidas = 0
    
    try:
        notificacoes_nao_lidas = request.user.notificacoes.filter(lida=False).count()
    except AttributeError:
        notificacoes_nao_lidas = 0

    if request.method == "POST":
        cultura_nome = request.POST.get("cultura", "").strip()
        umidade_raw = request.POST.get("umidade", "0")
        ph_raw = request.POST.get("ph", "0")
        temperatura_raw = request.POST.get("temperatura", "0")

        if cultura_nome and umidade_raw and ph_raw and temperatura_raw:
            try:
                umidade = float(str(umidade_raw).replace(',', '.'))
                ph = float(str(ph_raw).replace(',', '.'))
                temperatura = float(str(temperatura_raw).replace(',', '.'))

                if umidade < 30: class_umidade = 'BAIXA'
                elif umidade > 80: class_umidade = 'ALTA'
                else: class_umidade = 'MEDIA'

                if ph < 5.5: class_ph = 'ACIDO'
                elif ph > 7.5: class_ph = 'ALCALINO'
                else: class_ph = 'NEUTRO'

                if temperatura < 18: class_temp = 'FRIA'
                elif temperatura > 35: class_temp = 'QUENTE'
                else: class_temp = 'IDEAL'

                rec_textos = []
                prioridade_rec = 'BAIXA'
                if class_umidade == 'BAIXA': 
                    rec_textos.append("Solo seco. Incremente os ciclos de irrigação.")
                    prioridade_rec = 'MEDIA'
                if class_ph == 'ACIDO': 
                    rec_textos.append("Solo ácido. Recomendada a calagem para correção.")
                    prioridade_rec = 'ALTA'
                if class_temp == 'QUENTE': 
                    rec_textos.append("Solo superaquecido. Monitore estresse térmico da planta.")
                    prioridade_rec = 'URGENTE'
                
                recomendacao_final = " ".join(rec_textos) if rec_textos else "Solo estável e em ótimas condições operacionais."

                obj_cultura, _ = Cultura.objects.get_or_create(
                    nome=cultura_nome.capitalize(),
                    defaults={'descricao': f'Cultura de {cultura_nome.capitalize()} cadastrada via painel de monitoramento.'}
                )
                
                obj_propriedade = Propriedade.objects.first()
                if not obj_propriedade:
                    from .models import Produtor
                    produtor_padrao, _ = Produtor.objects.get_or_create(
                        cpf='000.000.000-00', 
                        defaults={'nome': 'Produtor Padrão', 'telefone': '0000', 'email': 'padrao@agro.com'}
                    )
                    obj_propriedade = Propriedade.objects.create(
                        produtor=produtor_padrao, nome='Propriedade Principal', localizacao='Geral', tamanho_hectares=10.0
                    )

                # TABELA 1: Analise
                Analise.objects.create(
                    usuario=request.user, cultura=cultura_nome.capitalize(),
                    umidade=umidade, ph=ph, temperatura=temperatura, recomendacao=recomendacao_final
                )

                # TABELA 2: UmidadeSolo
                reg_umidade = UmidadeSolo.objects.create(valor=umidade, classificacao=class_umidade)

                # TABELA 3: TemperaturaSolo
                reg_temp = TemperaturaSolo.objects.create(valor=temperatura, classificacao=class_temp)

                # TABELA 4: PhSolo
                reg_ph = PhSolo.objects.create(valor=ph, classificacao=class_ph)

                # TABELA 5: Recomendacao
                reg_rec = Recomendacao.objects.create(
                    titulo=f"Recomendação para {cultura_nome.capitalize()}",
                    descricao=recomendacao_final, prioridade=prioridade_rec
                )

                # TABELA 6: AnaliseSolo
                AnaliseSolo.objects.create(
                    cultura=obj_cultura, propriedade=obj_propriedade,
                    umidade=reg_umidade, ph=reg_ph, temperatura=reg_temp, recomendacao=reg_rec
                )

                # TABELA 7: Histórico Agrícola
                Historico.objects.create(
                    propriedade=obj_propriedade,
                    descricao=f"Leitura de parâmetros executada para a cultura {obj_cultura.nome}."
                )

                # TABELA 8: Relatório Automático
                Relatorio.objects.create(
                    titulo=f"Relatório Técnico - {cultura_nome.capitalize()} ({timezone.now().strftime('%d/%m/%Y')})",
                    descricao=f"Análise estrutural processada. pH verificado: {ph} ({class_ph}). Umidade: {umidade}% ({class_umidade}).",
                    propriedade=obj_propriedade
                )

                # TABELA 9: Notificação de Sistema
                if prioridade_rec in ['ALTA', 'URGENTE']:
                    Notificacao.objects.create(
                        usuario=request.user,
                        mensagem=f"Alerta crítico na cultura de {cultura_nome.capitalize()}: Índices fora da janela ideal!",
                        lida=False
                    )

                messages.success(request, 'Sucesso! Registros distribuídos e salvos em todos os módulos correlacionados.')
                return redirect('monitoramento')

            except ValueError:
                erro = "Por favor, insira numerações válidas nos campos de medição."
        else:
            erro = "Preencha todos os campos do formulário para prosseguir."

    # Coleta para exibição na página
    analises = Analise.objects.filter(usuario=request.user).order_by("-id")
    ultima_analise = analises.first() if analises.exists() else None

    ph_porcentagem = (float(ultima_analise.ph) / 14.0) * 100 if ultima_analise else 0
    temp_porcentagem = (float(ultima_analise.temperatura) / 50.0) * 100 if ultima_analise else 0

    context = {
        "notificacoes_nao_lidas": notificacoes_nao_lidas,
        "analises": analises,
        "ultima_analise": ultima_analise,
        "ph_porcentagem": ph_porcentagem,
        "temp_porcentagem": temp_porcentagem,
        "erro": erro
    }
    return render(request, "monitoramento/monitoramento.html", context)