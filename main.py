import sys
import time
import re
from src.evaluator import Evaluator
from src.chain import AssistantChain
# ATENÇÃO: QUANDO O ARQUIVO guardrails.py ESTIVER PRONTO, 
# DESCOMENTE A LINHA ABAIXO E APAGUE A CLASSE MockGuardrails INTEIRA.
# from src.guardrails import GuardrailSystem

def limpar_markdown_json(json_str):
    """Remove blocos de markdown da resposta do LLM."""
    json_str = json_str.strip()
    if json_str.startswith("```"):
        try:
            json_str = json_str.split("\n", 1)[1].rsplit("```", 1)[0]
        except IndexError:
            pass
    return json_str

# ==============================================================
# MOCK DOS GUARDRAILS
# ==============================================================
class MockGuardrails:
    def validar_input(self, texto):
        if len(texto) > 500: return False, "Texto muito longo."
        return True, "Seguro"
    def validar_output(self, resposta):
        return True, "Seguro"
# ==============================================================

def run_pipeline(texto_usuario, guardrails, chain):
    is_safe_input, _ = guardrails.validar_input(texto_usuario)
    if not is_safe_input: return True, "none", False, "Bloqueado"

    try:
        classificacao_obj = chain.etapa1_classificar(texto_usuario)
        processamento_obj = chain.etapa2_processar(texto_usuario, classificacao_obj)
        resposta_obj = chain.etapa3_responder(classificacao_obj, processamento_obj)
        resposta_bruta = limpar_markdown_json(resposta_obj.resposta)
        return False, classificacao_obj.tipo, True, resposta_bruta
    except Exception as e:
        return False, "erro", False, str(e)

if __name__ == "__main__":
    guardrails = MockGuardrails()
    chain = AssistantChain()
    
    escolha = input("1 - Chat, 2 - Avaliação: ")
    if escolha == '2':
        evaluator = Evaluator()
        evaluator.run_evaluation(lambda t: run_pipeline(t, guardrails, chain))