def notificacoes(request):
    if request.user.is_authenticated:
        qtd = request.user.notificacoes.filter(lida=False).count()
    else:
        qtd = 0

    return {
        'notificacoes_nao_lidas': qtd
    }