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

]