import os
import time
from dotenv import load_dotenv
from ollama import Client

load_dotenv() # Carrega variáveis do arquivo .env utilizados pela conexão com Ollama
api_key = os.getenv("OLLAMA_API_KEY")

class LLMClient:
    def __init__(self): 
        self.host = os.getenv("OLLAMA_HOST", "https://ollama.com").rstrip("/") # Determina o host do modelo
        self.model = os.getenv("OLLAMA_MODEL", "gpt-oss:120b") 
        self.max_retries = int(os.getenv("OLLAMA_MAX_RETRIES", "3")) # Determina número máximo de tentativas - 3x
        
        self.client = Client(
            host=self.host,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def chat(self, prompt, system="", temp=0.3, max_tokens=800): 
        
        """
                Envia mensagens ao modelo via endpoint /api/chat do Ollama.

                Parâmetros esperados:
                - Prompt do usuário validado pelo guardrail

                - System prompt defensivo do system_prompt.txt (aula 10)
                
                - Pattern prompt de acordo com a tarefa detectada pelo chain

                - temp:
                    Temperatura da inferência.
                    Controla criatividade/variabilidade da resposta.

                - max_tokens:
                    Quantidade máxima de tokens gerados pelo modelo.

                Retorno:
                dict contendo:
                - resposta do modelo
                - tokens do prompt
                - tokens da resposta
                - tempo total da inferência
        """


        if not prompt or not prompt.strip():
            raise ValueError("O prompt não pode ser vazio.")

        messages = []
        if system and system.strip():
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        last_error = None # Armazena o último erro ocorrido durante retries

        for attempt in range(self.max_retries): # Tenta o máximo número de vezes fazer o request (3x)
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        "temperature": temp,
                        "num_predict": max_tokens
                    },
                    stream=False
                )
                

                return {
                    "resposta": response["message"]["content"].strip(),
                    "tokens_prompt": response.get("prompt_eval_count", 0),
                    "tokens_resposta": response.get("eval_count", 0)
                }

            except (KeyError, ValueError) as e:
                last_error = f"Erro ao interpretar resposta da API: {e}"
                break

            except Exception as e:
                last_error = f"Erro na tentativa {attempt + 1}: {e}"

            time.sleep(2 ** attempt) # Retry Exponencial: mais tentavias --> maior espera para a próxima tentativa

        return { # Retorno padronizado em caso de falha total
            "resposta": f"Erro: {last_error}",
            "tokens_prompt": 0,
            "tokens_resposta": 0,
        }