import sys
import time
import re
from src.evaluator import Evaluator
from src.chain import AssistantChain

# ATENÇÃO: QUANDO O ARQUIVO guardrails.py ESTIVER PRONTO, 
# DESCOMENTE A LINHA ABAIXO E APAGUE A CLASSE MockGuardrails INTEIRA.
# from src.guardrails import GuardrailSystem

def limpar_markdown_json(json_str):
    """
    Remove blocos de markdown da resposta do LLM antes de exibir ao usuário.
    """
    json_str = json_str.strip()
    if json_str.startswith("```"):
        try:
            json_str = json_str.split("\n", 1)[1].rsplit("
```", 1)[0]
        except IndexError:
            pass
    return json_str

# ==============================================================
# MOCK DOS GUARDRAILS
# ==============================================================
class MockGuardrails:
    def validar_input(self, texto):
        texto_lower = texto.lower()
        if len(texto) > 500:
            return False, "Texto muito longo (> 500 caracteres)."
        if re.search(r"[<>{}]", texto):
            return False, "Caracteres proibidos encontrados."
            
        padroes_ataque = ["ignore", "esqueça", "jailbreak", "dan", "revelando", "override", "imprima", "system prompt"]
        for padrao in padroes_ataque:
            if padrao in texto_lower:
                return False, f"Possível tentativa de Prompt Injection detectada ({padrao})."
        return True, "Seguro"

    def validar_output(self, resposta):
        if "regras e limites invioláveis" in resposta.lower() or "contexto: você é" in resposta.lower():
             return False, "Vazamento de System Prompt."
        return True, "Seguro"
# ==============================================================

def run_pipeline(texto_usuario, guardrails, chain):
    """
    Executa o fluxo de chaining exigido:
    Input Guard -> Etapa 1 -> Etapa 2 -> Etapa 3 -> Output Guard.
    Retorna: (is_blocked, classificacao, json_valido, resposta_final)
    """
    # 1. Input Guard
    is_safe_input, motivo_input = guardrails.validar_input(texto_usuario)
    if not is_safe_input:
        return True, "none", False, f"Bloqueado (Input): {motivo_input}"

    try:
        classificacao_obj = chain.etapa1_classificar(texto_usuario)
        tipo_classificacao = classificacao_obj.tipo 

        processamento_obj = chain.etapa2_processar(texto_usuario, classificacao_obj)
        
        resposta_obj = chain.etapa3_responder(classificacao_obj, processamento_obj)
        
        resposta_bruta = limpar_markdown_json(resposta_obj.resposta)
        
        json_valido = True 

    except Exception as e:
        return False, "erro", False, f"Erro no processamento estruturado: {str(e)}"

    is_safe_output, motivo_output = guardrails.validar_output(resposta_bruta)
    if not is_safe_output:
        return True, tipo_classificacao, json_valido, f"Bloqueado (Output): {motivo_output}"

    return False, tipo_classificacao, json_valido, resposta_bruta

def modo_interativo():
    print("=== Smart Assistant: Modo Interativo ===")
    print("Digite 'sair' para encerrar.")
    
    guardrails = MockGuardrails() # Quando estiver pronto, mude para: GuardrailSystem()
    chain = AssistantChain()

    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() == 'sair':
            break
            
        print("\nProcessando (isso pode levar alguns segundos)...")
        inicio = time.time()
        
        is_blocked, tipo, _, resposta = run_pipeline(user_input, guardrails, chain)
        
        tempo_decorrido = time.time() - inicio
        
        if is_blocked:
            print(f"🛑 SEGURANÇA: {resposta} (⏱️ {tempo_decorrido:.2f}s)")
        else:
            print(f"[{tipo.upper()}] 🤖 Assistente: {resposta} (⏱️ {tempo_decorrido:.2f}s)")

def modo_avaliacao():
    print("=== Iniciando Avaliação Automática ===")
    print("Atenção: A avaliação requer diversas chamadas ao LLM e pode demorar.")
    
    guardrails = MockGuardrails() # Quando estiver pronto, mude para: GuardrailSystem()
    chain = AssistantChain()
    
    def mock_pipeline_func(texto):
        return run_pipeline(texto, guardrails, chain)
        
    avaliador = Evaluator()
    avaliador.run_evaluation(mock_pipeline_func)

if __name__ == "__main__":
    print("Escolha o modo de execução:")
    print("1 - Interativo (Chat)")
    print("2 - Avaliação Automática (Gera gráficos e relatórios)")
    
    escolha = input("\nOpção: ")
    if escolha == '1':
        modo_interativo()
    elif escolha == '2':
        modo_avaliacao()
    else:
        print("Opção inválida.")