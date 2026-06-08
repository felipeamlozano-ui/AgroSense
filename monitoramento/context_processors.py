from .models import Notificacao

def notificacoes(request):
    if request.user.is_authenticated:

        todas_notificacoes = request.user.notificacoes.all()

        notificacoes_nao_lidas = todas_notificacoes.filter(
            lida=False
        ).count()

        notificacoes = todas_notificacoes.order_by(
            '-data_envio'
        )[:10]

        return {
            'notificacoes': notificacoes,
            'notificacoes_nao_lidas': notificacoes_nao_lidas
        }

    return {
        'notificacoes': [],
        'notificacoes_nao_lidas': 0
    }