# Smart Assistant - CP03
Projeto de Assistente Inteligente com Chaining e Guardrails.

## Estrutura
- `main.py`: Orquestrador principal.
- `src/`: Lógica do chain, avaliador e guardrails.
- `output/`: Relatórios de avaliação (CSV).
- `graficos/`: Visualização das métricas.

## Execução
1. Instale dependências: `pip install pandas matplotlib pydantic ollama`
2. Rode a avaliação: `python main.py`