import json
import time
import os
import pandas as pd
import matplotlib.pyplot as plt

class Evaluator:
    def __init__(self, dataset_path="data/test_dataset.json"):
        self.dataset_path = dataset_path
        os.makedirs("output", exist_ok=True)
        os.makedirs("output/graficos", exist_ok=True)

    def load_dataset(self):
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def run_evaluation(self, pipeline_func):
        """
        Executa o pipeline para cada item do dataset e coleta métricas.
        pipeline_func: Função que executa o processamento do LLM.
        """
        dataset = self.load_dataset()
        results = []

        print(f"Iniciando avaliação com {len(dataset)} itens...")

        for item in dataset:
            inicio = time.time()
            
            try:
                is_blocked, tipo, success, resposta = pipeline_func(item['texto'])
                fim = time.time()
                
                results.append({
                    "id": item['id'],
                    "categoria": item.get('tipo_esperado', 'N/A'),
                    "tempo_resposta": round(fim - inicio, 4),
                    "sucesso": success,
                    "bloqueado": is_blocked
                })
            except Exception as e:
                print(f"Erro no item {item['id']}: {e}")

        self.salvar_resultados(results)
        print("Avaliação finalizada e relatórios gerados em 'output/'!")

    def salvar_resultados(self, resultados_lista):
        df = pd.DataFrame(resultados_lista)
        df.to_csv("output/eval_results.csv", index=False)
        
        df_resumo = df.groupby('categoria').agg({
            'id': 'count',
            'tempo_resposta': 'mean'
        }).rename(columns={'id': 'total_testes'})
        
        df_resumo.to_csv("output/graficos.csv", index=False)
        
        plt.figure(figsize=(8, 5))
        df_resumo['total_testes'].plot(kind='bar', color='skyblue')
        plt.title("Distribuição de Testes por Categoria")
        plt.ylabel("Quantidade")
        plt.savefig("output/graficos/metricas_avaliacao.png")
        plt.close()