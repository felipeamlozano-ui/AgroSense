import google.generativeai as genai

genai.configure(api_key="AQ.Ab8RN6KaHdryNZO4FlzNPTkgcvvKU5SlP7Lfvout09DtorC54g")

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 1200
    }
)


def gerar_relatorio_ia(cultura, dados_solo, referencia_embrapa):

    umidade_ideal = referencia_embrapa.get("umidade_ideal", (40, 60))
    ph_ideal = referencia_embrapa.get("ph_ideal", (5.5, 6.5))
    temperatura_ideal = referencia_embrapa.get("temperatura_ideal", (20, 30))

    prompt = f"""
Você é um engenheiro agrônomo sênior da EMBRAPA especializado em análise de solo.

Gere um RELATÓRIO TÉCNICO AGRÍCOLA em TEXTO CORRIDO.

REGRAS IMPORTANTES:
- Não use JSON
- Não use HTML
- Não use listas longas
- Não use markdown
- Escreva em parágrafos curtos
- Linguagem técnica, mas fácil de entender
- 20 a 30 linhas no total
- Estrutura lógica obrigatória

---

CULTURA: {cultura}

DADOS DO SOLO:
- Umidade: {dados_solo.get("umidade")}%
- pH: {dados_solo.get("ph")}
- Temperatura: {dados_solo.get("temperatura")}°C

REFERÊNCIA EMBRAPA:
- Umidade ideal: {umidade_ideal}
- pH ideal: {ph_ideal}
- Temperatura ideal: {temperatura_ideal}

---

FORMATO OBRIGATÓRIO DO TEXTO:

1. Diagnóstico do solo (2–3 linhas)
2. Comparação com referência (3–5 linhas)
3. Problemas identificados (3–5 linhas)
4. Impacto na cultura (3–5 linhas)
5. Recomendações técnicas (4–6 linhas)
6. Produtos recomendados (2–4 linhas)
7. Conclusão técnica (2–3 linhas)

---

IMPORTANTE:
Se tudo estiver adequado, informe isso claramente e recomende apenas manutenção preventiva.
"""

    response = model.generate_content(prompt)

    return response.text.strip()