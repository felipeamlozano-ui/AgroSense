from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm


class UsuarioLoginView(LoginView):
    template_name = 'monitoramento/login.html'
    authentication_form = CustomLoginForm

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        # =========================
        # LOGIN
        # =========================
        if action == "login":
            form = self.get_form()

            if form.is_valid():
                login(request, form.get_user())
                return redirect("index")

            messages.error(request, "Usuário ou senha inválidos.")
            return self.form_invalid(form)

        # =========================
        # CADASTRO
        # =========================
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


def index(request):
    try:
        analises = Analise.objects.all()
        erro = None
    except Exception as e:
        analises = []
        erro = str(e)

    return render(request, "monitoramento/index.html", {
        "analises": analises,
        "erro": erro
    })


def cadastrar(request):
    if request.method == "POST":
        try:
            Analise.objects.create(
                cultura=request.POST.get("cultura", "Milho"),
                umidade=float(request.POST.get("umidade", 0)),
                ph=float(request.POST.get("ph", 0)),
                temperatura=float(request.POST.get("temperatura", 0)),
                recomendacao="Análise gerada automaticamente"
            )
        except Exception as e:
            print("🔥 ERRO AO SALVAR:", e)

        return redirect("index")

    return render(request, "monitoramento/cadastrar.html")


@login_required
def monitoramento(request):
    notificacoes_nao_lidas = 0

    if request.user.is_authenticated:
        notificacoes_nao_lidas = request.user.notificacoes.filter(lida=False).count()

    return render(request, "monitoramento/monitoramento.html", {
        "notificacoes_nao_lidas": notificacoes_nao_lidas
    })