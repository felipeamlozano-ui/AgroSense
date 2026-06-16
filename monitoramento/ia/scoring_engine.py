# monitoramento/ia/scoring/score_engine.py

from dataclasses import dataclass
from typing import Dict, List


# ==========================================
# CONFIGURAÇÕES CORPORATIVAS
# ==========================================

PESO_PH = 40
PESO_UMIDADE = 35
PESO_TEMPERATURA = 25

SEVERIDADE_BAIXA = "BAIXA"
SEVERIDADE_MEDIA = "MEDIA"
SEVERIDADE_ALTA = "ALTA"
SEVERIDADE_CRITICA = "CRITICA"


# ==========================================
# DTOs
# ==========================================

@dataclass
class IndicadorScore:
    nome: str
    valor: float
    minimo: float
    maximo: float
    score: int
    status: str
    severidade: str
    observacao: str


# ==========================================
# ENGINE
# ==========================================

class ScoreEngine:

    @classmethod
    def _calcular_desvio_percentual(cls, valor, minimo, maximo):
        centro = (minimo + maximo) / 2
        if centro == 0:
            return 0
        # Força os três valores a serem float antes de calcular para evitar o erro de tipo
        return abs((float(valor) - float(maximo)) / float(centro)) * 100
    @staticmethod
    def _classificar_severidade(
        desvio: float
    ):

        if desvio == 0:
            return SEVERIDADE_BAIXA

        if desvio <= 10:
            return SEVERIDADE_BAIXA

        if desvio <= 25:
            return SEVERIDADE_MEDIA

        if desvio <= 50:
            return SEVERIDADE_ALTA

        return SEVERIDADE_CRITICA

    @staticmethod
    def _calcular_score_individual(
        valor,
        minimo,
        maximo
    ):

        desvio = ScoreEngine._calcular_desvio_percentual(
            valor,
            minimo,
            maximo
        )

        score = max(
            0,
            int(100 - desvio * 2)
        )

        severidade = ScoreEngine._classificar_severidade(
            desvio
        )

        if valor < minimo:

            status = "ABAIXO"

            observacao = (
                f"Valor abaixo da faixa recomendada "
                f"({minimo}-{maximo})"
            )

        elif valor > maximo:

            status = "ACIMA"

            observacao = (
                f"Valor acima da faixa recomendada "
                f"({minimo}-{maximo})"
            )

        else:

            status = "ADEQUADO"

            observacao = (
                "Valor dentro da faixa ideal."
            )

        return score, status, severidade, observacao

    @classmethod
    def analisar(
        cls,
        dados: Dict,
        referencia: Dict
    ):

        indicadores: List[IndicadorScore] = []

        # ======================
        # PH
        # ======================

        score, status, severidade, obs = (
            cls._calcular_score_individual(
                dados["ph"],
                referencia["ph_ideal"][0],
                referencia["ph_ideal"][1]
            )
        )

        indicadores.append(
            IndicadorScore(
                nome="pH",
                valor=dados["ph"],
                minimo=referencia["ph_ideal"][0],
                maximo=referencia["ph_ideal"][1],
                score=score,
                status=status,
                severidade=severidade,
                observacao=obs
            )
        )

        # ======================
        # UMIDADE
        # ======================

        score, status, severidade, obs = (
            cls._calcular_score_individual(
                dados["umidade"],
                referencia["umidade_ideal"][0],
                referencia["umidade_ideal"][1]
            )
        )

        indicadores.append(
            IndicadorScore(
                nome="Umidade",
                valor=dados["umidade"],
                minimo=referencia["umidade_ideal"][0],
                maximo=referencia["umidade_ideal"][1],
                score=score,
                status=status,
                severidade=severidade,
                observacao=obs
            )
        )

        # ======================
        # TEMPERATURA
        # ======================

        score, status, severidade, obs = (
            cls._calcular_score_individual(
                dados["temperatura"],
                referencia["temperatura_ideal"][0],
                referencia["temperatura_ideal"][1]
            )
        )

        indicadores.append(
            IndicadorScore(
                nome="Temperatura",
                valor=dados["temperatura"],
                minimo=referencia["temperatura_ideal"][0],
                maximo=referencia["temperatura_ideal"][1],
                score=score,
                status=status,
                severidade=severidade,
                observacao=obs
            )
        )

        # ======================
        # SCORE PONDERADO
        # ======================

        ph_score = indicadores[0].score
        umidade_score = indicadores[1].score
        temperatura_score = indicadores[2].score

        score_final = int(

            (ph_score * PESO_PH +
             umidade_score * PESO_UMIDADE +
             temperatura_score * PESO_TEMPERATURA)

            /

            (PESO_PH +
             PESO_UMIDADE +
             PESO_TEMPERATURA)

        )

        # ======================
        # CLASSIFICAÇÃO
        # ======================

        if score_final >= 90:

            classificacao = "EXCELENTE"

        elif score_final >= 80:

            classificacao = "MUITO_BOM"

        elif score_final >= 70:

            classificacao = "BOM"

        elif score_final >= 60:

            classificacao = "ATENCAO"

        elif score_final >= 40:

            classificacao = "RISCO_ALTO"

        else:

            classificacao = "CRITICO"

        # ======================
        # ALERTAS
        # ======================

        alertas = []

        for indicador in indicadores:

            if indicador.severidade in (
                SEVERIDADE_ALTA,
                SEVERIDADE_CRITICA
            ):

                alertas.append(
                    f"{indicador.nome}: "
                    f"{indicador.observacao}"
                )

        # ======================
        # RESULTADO FINAL
        # ======================

        return {

            "score_final": score_final,

            "classificacao": classificacao,

            "alertas": alertas,

            "indicadores": [

                {
                    "nome": i.nome,
                    "valor": i.valor,
                    "score": i.score,
                    "status": i.status,
                    "severidade": i.severidade,
                    "observacao": i.observacao
                }

                for i in indicadores

            ]
        }