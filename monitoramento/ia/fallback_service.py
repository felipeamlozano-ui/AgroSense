def gerar_relatorio_fallback(
    cultura,
    dados_solo,
    diagnosticos,
    score,
    classificacao,
    risco
):

    return f"""
RELATÓRIO TÉCNICO AGRÍCOLA

Cultura:
{cultura}

Parâmetros observados:

Umidade: {dados_solo['umidade']}%
pH: {dados_solo['ph']}
Temperatura: {dados_solo['temperatura']}°C

Diagnósticos:

{chr(10).join("- " + d for d in diagnosticos)}

Indicadores:

Score Agronômico: {score}
Classificação: {classificacao}
Nível de Risco: {risco}

O relatório foi produzido utilizando regras de negócio internas devido à indisponibilidade temporária do serviço de inteligência artificial.

Recomenda-se acompanhamento contínuo dos parâmetros monitorados para garantir estabilidade produtiva e suporte à tomada de decisão.

Conclusão:

A propriedade deve manter monitoramento periódico dos indicadores avaliados para reduzir riscos operacionais e preservar o potencial produtivo da cultura.
"""