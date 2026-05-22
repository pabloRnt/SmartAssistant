import json
from src.llm_client import LLMClient
import src.prompts as prompts
from src.schemas import ClassificacaoSchema, ProcessamentoSchema, RespostaSchema
from pydantic import ValidationError

class AssistantChain:
    def __init__(self):
        self.llm = LLMClient()
        self.max_retries = 3

    def _extrair_json_da_string(self, texto: str) -> dict:
        """Busca chaves e converte strings de resposta do LLM para dicionário."""
        try:
            inicio = texto.find('{')
            fim = texto.rfind('}') + 1
            if inicio != -1 and fim != 0:
                return json.loads(texto[inicio:fim])
        except json.JSONDecodeError:
            pass
        return None

    def _executar_com_retry(self, prompt: str, schema_class, temperatura: float):
        """Tenta obter uma resposta estruturada válida do LLM até o limite de retries."""
        for _ in range(self.max_retries):
            resultado = self.llm.chat(prompt=prompt, temp=temperatura)
            dados_brutos = self._extrair_json_da_string(resultado["resposta"])
            
            if dados_brutos:
                try:
                    return schema_class(**dados_brutos)
                except ValidationError:
                    continue
        return None

    def etapa1_classificar(self, texto: str) -> ClassificacaoSchema:
        prompt = prompts.prompt_classificar(texto)
        resultado = self._executar_com_retry(prompt, ClassificacaoSchema, 0.1)
        
        if resultado:
            return resultado
        
        # Fallback seguro caso as 3 tentativas falhem
        return ClassificacaoSchema(tipo="duvida", urgencia="media", tema="Geral")

    def etapa2_processar(self, texto: str, classificacao: ClassificacaoSchema) -> ProcessamentoSchema:
        # Lógica Condicional: A etapa 2 varia de acordo com o resultado da etapa 1
        if classificacao.tipo == "reclamacao":
            prompt = prompts.prompt_processarReclamacao(texto, classificacao.tema, classificacao.urgencia)
        elif classificacao.tipo == "devolucao":
            prompt = prompts.prompt_processarDevolucao(texto, classificacao.tema)
        else:
            prompt = prompts.prompt_processarDuvida(texto, classificacao.tema, classificacao.urgencia)

        # Adicionamos instrução para forçar saída estruturada nesta etapa
        prompt += "\n\nRetorne APENAS um JSON válido contendo as chaves 'dados_extraidos' (objeto) e 'analise' (string)."
        
        resultado = self._executar_com_retry(prompt, ProcessamentoSchema, 0.2)
        
        if resultado:
            return resultado
            
        # Fallback
        return ProcessamentoSchema(dados_extraidos={}, analise="Não foi possível processar os dados detalhadamente.")

    def etapa3_responder(self, classificacao: ClassificacaoSchema, processamento: ProcessamentoSchema) -> RespostaSchema:
        prompt = prompts.prompt_responder(classificacao, processamento.analise)
        resultado = self._executar_com_retry(prompt, RespostaSchema, 0.4)
        
        if resultado:
            return resultado
            
        # Fallback
        return RespostaSchema(resposta="Desculpe, ocorreu um erro sistêmico. Por favor, tente novamente.", confianca="baixa", acao_sugerida="Nenhuma")

    def executar_pipeline(self, texto: str) -> str:
        """Função orquestradora para o main.py chamar."""
        classificacao = self.etapa1_classificar(texto)
        processamento = self.etapa2_processar(texto, classificacao)
        resposta_final = self.etapa3_responder(classificacao, processamento)
        
        return resposta_final.resposta