def calcular_risco(
    dados,
    referencia
):

    risco = 0

    if dados["ph"] < referencia["ph_ideal"][0]:
        risco += 1

    if dados["ph"] > referencia["ph_ideal"][1]:
        risco += 1

    if dados["umidade"] < referencia["umidade_ideal"][0]:
        risco += 1

    if dados["umidade"] > referencia["umidade_ideal"][1]:
        risco += 1

    if dados["temperatura"] < referencia["temperatura_ideal"][0]:
        risco += 1

    if dados["temperatura"] > referencia["temperatura_ideal"][1]:
        risco += 1

    if risco == 0:
        return "BAIXO"

    if risco <= 2:
        return "MODERADO"

    if risco <= 4:
        return "ALTO"

    return "CRITICO"