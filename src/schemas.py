from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ClassificacaoSchema(BaseModel):
    tipo: str = Field(description="reclamacao|duvida|devolucao|elogio|sugestao")
    urgencia: str = Field(description="alta|media|baixa")
    tema: str = Field(description="Tema principal da solicitação do usuário")

class ProcessamentoSchema(BaseModel):
    dados_extraidos: Dict[str, Any] = Field(
        description="Dicionário com os dados fundamentais extraídos da solicitação", 
        default_factory=dict
    )
    analise: str = Field(description="Análise textual do problema ou solicitação")
    sentimento: Optional[str] = Field(
        description="Sentimento do cliente identificado no texto", 
        default=None
    )

class RespostaSchema(BaseModel):
    resposta: str = Field(description="Resposta final formatada para o cliente")
    confianca: str = Field(description="alta|media|baixa")
    acao_sugerida: str = Field(description="Próxima ação sugerida que o cliente deve tomar")