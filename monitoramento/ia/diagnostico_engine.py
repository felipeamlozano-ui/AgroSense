from typing import Dict, List


def gerar_diagnosticos(
    dados_solo: Dict,
    referencia: Dict
) -> List[str]:

    diagnosticos = []

    ph = dados_solo["ph"]
    umidade = dados_solo["umidade"]
    temperatura = dados_solo["temperatura"]

    ph_ideal = referencia["ph_ideal"]
    umidade_ideal = referencia["umidade_ideal"]
    temperatura_ideal = referencia["temperatura_ideal"]

    if ph < ph_ideal[0]:
        diagnosticos.append(
            "Solo com acidez acima da recomendada."
        )

    elif ph > ph_ideal[1]:
        diagnosticos.append(
            "Solo com alcalinidade acima da recomendada."
        )

    else:
        diagnosticos.append(
            "pH dentro da faixa ideal."
        )

    if umidade < umidade_ideal[0]:
        diagnosticos.append(
            "Baixa disponibilidade hídrica."
        )

    elif umidade > umidade_ideal[1]:
        diagnosticos.append(
            "Excesso de umidade."
        )

    else:
        diagnosticos.append(
            "Umidade adequada."
        )

    if temperatura < temperatura_ideal[0]:
        diagnosticos.append(
            "Temperatura abaixo do ideal."
        )

    elif temperatura > temperatura_ideal[1]:
        diagnosticos.append(
            "Temperatura acima do ideal."
        )

    else:
        diagnosticos.append(
            "Temperatura adequada."
        )

    return diagnosticos