from django.shortcuts import render, redirect
from .models import Analise


def index(request):
    """
    Página inicial do dashboard.
    Protegida contra erro de banco/migração.
    """

    try:
        analises = list(Analise.objects.all())
        erro = None

    except Exception as e:
        # Isso vai aparecer no terminal (MUITO importante pra debug)
        print("🔥 ERRO AO ACESSAR BANCO:", e)

        analises = []
        erro = str(e)

    context = {
        "analises": analises,
        "erro": erro
    }

    return render(request, "monitoramento/index.html", context)


def cadastrar(request):
    """
    Página simples de teste para criar registros manualmente.
    (se você ainda não tiver formulário pronto)
    """

    if request.method == "POST":
        try:
            Analise.objects.create(
                cultura=request.POST.get("cultura", "Milho"),
                umidade=request.POST.get("umidade", 0),
                ph=request.POST.get("ph", 0),
                temperatura=request.POST.get("temperatura", 0),
                recomendacao="Análise gerada automaticamente"
            )
        except Exception as e:
            print("🔥 ERRO AO SALVAR:", e)

        return redirect("/")

    return render(request, "monitoramento/cadastrar.html")