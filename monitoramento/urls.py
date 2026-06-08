from django.urls import path
from . import views
from .views import UsuarioLoginView

urlpatterns = [

    path(
        '',
        views.index,
        name='index'
    ),

    path(
        'cadastrar/',
        views.cadastro,
        name='cadastro'
    ),

    path(
        'monitoramento/',
        views.monitoramento,
        name='monitoramento'
    ),

    path(
        'login/',
        UsuarioLoginView.as_view(),
        name='login'
    ),

    path(
        'notificacao/<int:notificacao_id>/',
        views.detalhe_notificacao,
        name='detalhe_notificacao'
    ),

    path(
        'notificacoes/lidas/',
        views.marcar_todas_lidas,
        name='marcar_todas_lidas'
    ),
    path(
        'gestao/',
        views.gestao_agricola,
        name='gestao_agricola'
    ),

]