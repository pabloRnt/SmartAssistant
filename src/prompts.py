''' PENDÊNCIAS: 
- Ajustar como será a entrada do usuário validada
- Enviar prompts sequencialmente para llm_client
- Receber resp_classificar do modelo e usar no prompts.py
- Receber resp_processar
- 
'''


# === EXEMPLOS FEW-SHOT PARA CLASSIFICAÇÃO === 

EXEMPLOS_CLASSIFICACAO = """
Exemplo 1
Entrada:
"Meu notebook chegou com a tela quebrada e ninguém resolve meu problema."

Saída:
{
  "tipo": "reclamacao",
  "urgencia": "alta",
  "tema": "produto com defeito"
}

Exemplo 2
Entrada:
"O fone bluetooth possui garantia de quantos meses?"

Saída:
{
  "tipo": "duvida",
  "urgencia": "baixa",
  "tema": "garantia"
}

Exemplo 3
Entrada:
"Quero devolver meu monitor porque ele não atendeu minhas expectativas."

Saída:
{
  "tipo": "devolucao",
  "urgencia": "media",
  "tema": "devolucao de produto"
}

Exemplo 4
Entrada:
"Meu teclado veio quebrado e quero devolver imediatamente."

Saída:
{
  "tipo": "devolucao",
  "urgencia": "alta",
  "tema": "produto com defeito"
}

Exemplo 5
Entrada:
"Como funciona a política de troca da TechStore?"

Saída:
{
  "tipo": "duvida",
  "urgencia": "baixa",
  "tema": "politica de troca"
}

Exemplo 6
Entrada:
"Já faz duas semanas que meu pedido está atrasado e ninguém me responde."

Saída:
{
  "tipo": "reclamacao",
  "urgencia": "media",
  "tema": "atraso na entrega"
}
"""

# === ETAPA 1: CLASSIFICAÇÃO ===
# FRAMEWORK: RTF + FEWSHOTS

prompt_classificar = f"""
Com base nos exemplos abaixo:
{EXEMPLOS_CLASSIFICACAO}

Classifique a solicitação do cliente APENAS como:
- reclamacao
- duvida
- devolucao

Defina a urgência APENAS como:
- alta
- media
- baixa

Retorne APENAS um JSON válido no formato:

{{
  "tipo": "...",
  "urgencia": "...",
  "tema": "..."
}}

Entrada do cliente:
{inputUsuario_validado} 
"""

# === ETAPA 2: PROCESSAMENTO CONDICIONAL ===
''' FRAMEWORKS: 

- Reclamação: CRISPE + RECIPE PATTERN 
- Dúvida: CRISPE + RECIPE PATTERN
- Devolução: RECIPE PATTERN

'''

match resp_classificar.tipo:
    case "reclamacao": 
        prompt_processar = f'''
        Você deve entender o motivo da reclamação do usuário "{inputUsuario_validado}",
        considerando o tema "{resp_classificar[tema]}" e alinhando seu tom com a urgência "{resp_classificar[urgencia]}".

        Para explicar como o cliente pode resolver seu problema, SEMPRE siga:
        1. Identifique o problema.
        2. Identifique o produto envolvido.
        3. Analise o impacto para o cliente.
        4. Determine a melhor ação para resolução.
        5. Gere uma orientação clara para o cliente.
        '''
    case "duvida":
        prompt_processar =  f'''
        Responda à dúvida do cliente alinhando seu tom com urgência: "{resp_classificar[urgencia]}".


        "{inputUsuario_validado}"

        SEMPRE siga os passos:

        1. Considere o tema "{resp_classificar[tema]}".
        2. Identifique a dúvida principal do cliente.
        3. Determine a informação mais relevante para responder à dúvida.
        4. Gere a resposta clara e objetiva. 
        5. SEMPRE evite informações que não sejam necessárias para responder à pergunta.
        '''
    case "devolucao":
        prompt_processar = f'''
        Para a solicitação de devolução do cliente:

        "{inputUsuario_validado}"

        SEMPRE siga os passos:

        1. Identifique o produto envolvido.
        2. Identifique o motivo da devolução.
        3. Identifique quais ações o cliente deve realizar.
        4. Explique de forma clara como prosseguir com a devolução.
        5. Cite BREVEMENTE cuidados gerais que podem facilitar o processo de devolução.
        '''

# === ETAPA 3: RESPOSTA ===
# PATTERN: TEMPLATE PATTERN

prompt_responder = f'''
Utilize as informações abaixo para gerar a resposta final.

Tipo:
{resp_classificar[tipo]}

Tema:
{resp_classificar[tema]}

Conteúdo processado:
{resp_processar}

Retorne essas informações APENAS um JSON válido utilizando EXATAMENTE o template abaixo:

{{
    "tipo": "string",
    "tema": "string",
    "resposta": "string"
}}
'''
# Obs: O framework CRISPE é implementado pela combinação entre o system prompt e o prompt_processar.