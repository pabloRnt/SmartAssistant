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
# FRAMEWORKS: RTF + FEW-SHOT + TEMPLATE PATTERN

def prompt_classificar(inputUsuario_validado):
  return f"""
  Com base nos exemplos abaixo:

  {EXEMPLOS_CLASSIFICACAO}

  Tarefa:
  Classifique a solicitação do cliente.

  O campo "tipo" deve ser APENAS um dos valores:
  - reclamacao
  - duvida
  - devolucao

  O campo "urgencia" deve ser APENAS um dos valores:
  - alta
  - media
  - baixa

  O campo "tema" deve conter uma descrição curta do assunto principal da solicitação.

  Retorne APENAS um JSON válido.

  Não utilize markdown.
  Não utilize comentários.
  Não utilize explicações.
  Não adicione texto antes do JSON.
  Não adicione texto após o JSON.

  Formato obrigatório:

  {{
    "tipo": "...",
    "urgencia": "...",
    "tema": "..."
  }}

  Entrada do cliente:

  {inputUsuario_validado}
  """

# === ETAPA 2: PROCESSAMENTO CONDICIONAL ===
'''
FRAMEWORKS:

- Reclamação: CRISPE + RECIPE PATTERN
- Dúvida: CRISPE + RECIPE PATTERN
- Devolução: RECIPE PATTERN
'''

def prompt_processarReclamacao(inputUsuario_validado, tema, urgencia):
  return f'''
  Analise a reclamação do cliente:

  "{inputUsuario_validado}"

  Tema identificado:
  "{tema}"

  Nível de urgência:
  "{urgencia}"

  Para gerar a orientação ao cliente, siga OBRIGATORIAMENTE os passos abaixo:

  1. Identifique o problema.
  2. Identifique o produto envolvido.
  3. Analise o impacto para o cliente.
  4. Determine a melhor ação para resolução.
  5. Gere uma orientação clara para o cliente.

  Mantenha coerência com o tema informado.
  Considere a urgência ao definir o tom da resposta.
  Não invente informações.
  Não inclua conteúdo que não esteja relacionado à reclamação.
  '''

def prompt_processarDuvida(inputUsuario_validado, tema, urgencia):
  return f'''
  Responda à dúvida do cliente.

  Solicitação:

  "{inputUsuario_validado}"

  Tema identificado:
  "{tema}"

  Nível de urgência:
  "{urgencia}"

  Siga OBRIGATORIAMENTE os passos abaixo:

  1. Considere o tema "{tema}".
  2. Identifique a dúvida principal do cliente.
  3. Determine a informação mais relevante para responder à dúvida.
  4. Gere uma resposta clara e objetiva.
  5. Evite informações que não sejam necessárias para responder à pergunta.

  Considere a urgência ao definir o tom da resposta.
  Não invente informações.
  Não adicione explicações desnecessárias.
  '''

def prompt_processarDevolucao(inputUsuario_validado, tema):
  return f'''
  Analise a solicitação de devolução.

  Solicitação:

  "{inputUsuario_validado}"

  Tema identificado:
  "{tema}"

  Siga OBRIGATORIAMENTE os passos abaixo:

  1. Identifique o produto envolvido.
  2. Identifique o motivo da devolução.
  3. Identifique quais ações o cliente deve realizar.
  4. Explique de forma clara como prosseguir com a devolução.
  5. Cite brevemente cuidados gerais que podem facilitar o processo de devolução.

  Mantenha foco apenas na devolução.
  Não invente procedimentos.
  Não adicione informações irrelevantes.
  '''

# === ETAPA 3: RESPOSTA ===
# FRAMEWORKS: TEMPLATE PATTERN + STRUCTURED OUTPUT

def prompt_responder(classificacao, resp_processada):
  return f'''
  Utilize as informações abaixo para gerar a resposta final.

  Tipo:
  {classificacao.tipo}

  Tema:
  {classificacao.tema}

  Conteúdo processado:
  {resp_processada}

  Retorne APENAS um JSON válido.

  Não utilize markdown.
  Não utilize comentários.
  Não adicione texto antes do JSON.
  Não adicione texto após o JSON.

  Utilize EXATAMENTE o formato abaixo:

  {{
      "tipo": "string",
      "tema": "string",
      "resposta": "string"
  }}

  O campo "tipo" deve ser consistente com a classificação recebida.

  O campo "tema" deve ser consistente com o tema recebido.

  O campo "resposta" deve conter exclusivamente a resposta final ao cliente.
  '''