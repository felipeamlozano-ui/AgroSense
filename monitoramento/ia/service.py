from dotenv import load_dotenv

load_dotenv()

import os
import logging

from groq import Groq

from .validator import validar_dados
from .diagnostico_engine import gerar_diagnosticos
from .risk_engine import calcular_risco
from .scoring_engine import ScoreEngine
from .prompt_builder import montar_prompt
from .fallback_service import gerar_relatorio_fallback
from .constants import MODEL_NAME


# ==========================================================
# LOGGER
# ==========================================================

logger = logging.getLogger(__name__)


# ==========================================================
# CLIENTE GROQ
# ==========================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ==========================================================
# IA SERVICE
# ==========================================================

def gerar_relatorio_ia(
    cultura,
    dados_solo,
    referencia_embrapa
):

    diagnosticos = []
    score_resultado = None
    score = 0
    classificacao = "NÃO DEFINIDA"
    risco = "NÃO DEFINIDO"

    try:

        # ==========================================
        # VALIDAÇÃO
        # ==========================================

        validar_dados(dados_solo)

        # ==========================================
        # DIAGNÓSTICOS
        # ==========================================

        diagnosticos = gerar_diagnosticos(
            dados_solo,
            referencia_embrapa
        )

        # ==========================================
        # SCORE ENGINE
        # ==========================================

        score_resultado = ScoreEngine.analisar(
            dados_solo,
            referencia_embrapa
        )

        score = score_resultado["score_final"]

        classificacao = score_resultado["classificacao"]

        # ==========================================
        # RISCO
        # ==========================================

        risco = calcular_risco(
            dados_solo,
            referencia_embrapa
        )

        # ==========================================
        # PROMPT
        # ==========================================


        prompt = montar_prompt(
            cultura=cultura,
            dados_solo=dados_solo,
            referencia=referencia_embrapa,
            diagnosticos=diagnosticos,
            score=score,
            classificacao=classificacao,
            risco=risco
        )

        logger.info(
            f"[AGROSENSE] "
            f"Cultura={cultura} "
            f"Score={score} "
            f"Classificacao={classificacao} "
            f"Risco={risco}"
        )

        # ==========================================
        # IA
        # ==========================================

        resposta = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.1,
            max_tokens=1500,
            messages=[
                {
    "role": "system",
    "content": """
Você é um redator técnico corporativo especializado em agronegócio.

Sua função NÃO é analisar.

Sua função NÃO é diagnosticar.

Sua função NÃO é calcular.

A análise já foi concluída pelo sistema AgroSense.

Você apenas transforma resultados estruturados em um parecer técnico profissional.

Retorne apenas texto corrido.

Nunca utilize:

#
##
###
**
__
Markdown
Listas
Tabelas
Títulos
Subtítulos
<think>

Não revele raciocínio interno.
"""
},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        conteudo = resposta.choices[0].message.content

        # ==========================================
        # LIMPEZA DE THINKING
        # ==========================================

        if conteudo:

            while "<think>" in conteudo and "</think>" in conteudo:

                inicio = conteudo.find("<think>")
                fim = conteudo.find("</think>") + len("</think>")

                conteudo = (
                    conteudo[:inicio]
                    + conteudo[fim:]
                )

            conteudo = conteudo.strip()

        logger.info(
            f"[AGROSENSE] Relatório gerado com sucesso"
        )

        return conteudo

    except Exception as erro:

        import traceback
        logger.error(
            f"Falha na geração da análise: {str(erro)}"
        )
    
        print("\n===== ERRO IA =====")
        print(traceback.format_exc())
        print("===================\n")

        try:

            if not diagnosticos:

                diagnosticos = gerar_diagnosticos(
                    dados_solo,
                    referencia_embrapa
                )

            if score_resultado is None:

                score_resultado = ScoreEngine.analisar(
                    dados_solo,
                    referencia_embrapa
                )

            score = score_resultado["score_final"]

            classificacao = score_resultado["classificacao"]

            if risco == "NÃO DEFINIDO":

                risco = calcular_risco(
                    dados_solo,
                    referencia_embrapa
                )

        except Exception as fallback_error:

            logger.exception(
                f"[AGROSENSE] Erro secundário: {fallback_error}"
            )

        return gerar_relatorio_fallback(
            cultura=cultura,
            dados_solo=dados_solo,
            diagnosticos=diagnosticos,
            score=score,
            classificacao=classificacao,
            risco=risco
        )