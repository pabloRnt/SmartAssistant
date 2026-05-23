import json
import os
import time
import pandas as pd
import matplotlib.pyplot as plt

class Evaluator:
    def __init__(self, test_dataset_path="data/test_dataset.json", attack_dataset_path="data/attack_dataset.json"):
        self.test_dataset = self._load_json(test_dataset_path)
        self.attack_dataset = self._load_json(attack_dataset_path)
        
        os.makedirs("output", exist_ok=True)
        os.makedirs("graficos", exist_ok=True)

    def _load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo {path} não encontrado. Execute o script da raiz do projeto.")
            return []

    def run_evaluation(self, pipeline_func):
        resultados_legitimos = []
        resultados_ataques = []
        tempos_execucao = []
        
        print("\n📊 BENCHMARK DE PROMPTS — Avaliando Casos Legítimos (Consistência 3x)")
        for i, item in enumerate(self.test_dataset):
            print(f"Processando caso legítimo {i+1}/{len(self.test_dataset)}...")
            classificacoes = []
            
            inicio = time.time()
            
            for _ in range(3):
                is_blocked, classif, json_valido, _ = pipeline_func(item["texto"])
                classificacoes.append(str(classif).strip().lower())
                
            consistente = all(c == classificacoes[0] for c in classificacoes)

            is_blocked, classif, json_valido, res_final = pipeline_func(item["texto"])
            
            tempo_decorrido = time.time() - inicio
            tempos_execucao.append(tempo_decorrido)
            
            tipo_obtido = str(classif).strip().lower()
            tipo_esperado = item["tipo_esperado"].strip().lower()
            
            resultados_legitimos.append({
                "id": item["id"],
                "texto": item["texto"],
                "esperava_bloqueio": False,
                "foi_bloqueado": is_blocked,
                "json_valido": json_valido,
                "tipo_esperado": tipo_esperado,
                "tipo_obtido": tipo_obtido,
                "consistente_3x": consistente,
                "tempo_segundos": round(tempo_decorrido, 2)
            })

        print("\n--- Avaliando Ataques ---")
        for i, item in enumerate(self.attack_dataset):
            print(f"Processando ataque {i+1}/{len(self.attack_dataset)}...")
            inicio = time.time()
            is_blocked, classif, json_valido, _ = pipeline_func(item["texto"])
            tempo_decorrido = time.time() - inicio
            
            resultados_ataques.append({
                "id": item["id"],
                "texto": item["texto"],
                "tipo_ataque": item["tipo_ataque"],
                "esperava_bloqueio": True,
                "foi_bloqueado": is_blocked,
                "tempo_segundos": round(tempo_decorrido, 2)
            })

        self._gerar_relatorio(resultados_legitimos, resultados_ataques, tempos_execucao)

    def _gerar_relatorio(self, legitimos, ataques, tempos):
        df_legit = pd.DataFrame(legitimos)
        df_ataques = pd.DataFrame(ataques)
        
        df_completo = pd.concat([df_legit, df_ataques], ignore_index=True)
        df_completo.to_csv("output/eval_results.csv", index=False)

        acuracia_classificacao = (df_legit["tipo_esperado"] == df_legit["tipo_obtido"]).mean() * 100
        taxa_json_valido = df_legit["json_valido"].mean() * 100
        taxa_bloqueio = df_ataques["foi_bloqueado"].mean() * 100
        taxa_falso_positivo = df_legit["foi_bloqueado"].mean() * 100
        taxa_consistencia = df_legit["consistente_3x"].mean() * 100
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0

        print("\n=== MÉTRICAS DE AVALIAÇÃO ===")
        print(f"1. Acurácia de Classificação: {acuracia_classificacao:.2f}%")
        print(f"2. Taxa de JSON Válido: {taxa_json_valido:.2f}%")
        print(f"3. Taxa de Bloqueio (Ataques): {taxa_bloqueio:.2f}%")
        print(f"4. Taxa de Falso Positivo: {taxa_falso_positivo:.2f}%")
        print(f"5. Consistência (Mesma classe 3x): {taxa_consistencia:.2f}%")
        print(f"⏱️ Tempo médio por teste completo: {tempo_medio:.2f}s")

        metricas = ['Acurácia', 'JSON Válido', 'Bloqueio', 'Falsos Pos.', 'Consistência']
        valores = [acuracia_classificacao, taxa_json_valido, taxa_bloqueio, taxa_falso_positivo, taxa_consistencia]
        cores = ['#4CAF50', '#2196F3', '#F44336', '#FF9800', '#9C27B0']

        plt.figure(figsize=(10, 6))
        barras = plt.bar(metricas, valores, color=cores)
        plt.ylim(0, 110)
        plt.title('Métricas do Smart Assistant', fontsize=14)
        plt.ylabel('Porcentagem (%)')
        
        for barra in barras:
            altura = barra.get_height()
            plt.text(barra.get_x() + barra.get_width()/2., altura + 2,
                     f'{altura:.1f}%', ha='center', va='bottom', fontweight='bold')
            
        plt.savefig("graficos/metricas_avaliacao.png")
        print("\n✅ Gráfico salvo em 'graficos/metricas_avaliacao.png'.")
        print("✅ CSV salvo em 'output/eval_results.csv'.")