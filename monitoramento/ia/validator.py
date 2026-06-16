from .constants import *


def validar_dados(dados):

    obrigatorios = [
        "umidade",
        "ph",
        "temperatura"
    ]

    for campo in obrigatorios:

        if campo not in dados:
            raise ValueError(
                f"Campo obrigatório ausente: {campo}"
            )

        if dados[campo] is None:
            raise ValueError(
                f"Campo inválido: {campo}"
            )

    ph = float(dados["ph"])

    if ph < PH_MINIMO or ph > PH_MAXIMO:
        raise ValueError(
            "pH fora dos limites permitidos"
        )

    umidade = float(dados["umidade"])

    if umidade < UMIDADE_MINIMA or umidade > UMIDADE_MAXIMA:
        raise ValueError(
            "Umidade fora dos limites permitidos"
        )

    temperatura = float(dados["temperatura"])

    if (
        temperatura < TEMPERATURA_MINIMA
        or
        temperatura > TEMPERATURA_MAXIMA
    ):
        raise ValueError(
            "Temperatura fora dos limites permitidos"
        )