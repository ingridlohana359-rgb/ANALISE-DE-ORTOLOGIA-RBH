"""
visualizar_resultados.py

Lê o CSV de pares RBH gerado por reciprocal_best_hits.py e cria um
gráfico simples da distribuição dos e-values encontrados — útil para
ter uma primeira noção da força das correspondências encontradas.

Como usar:
    python visualizar_resultados.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

CAMINHO_CSV = os.path.join("results", "pares_rbh.csv")

df = pd.read_csv(CAMINHO_CSV)
print(f"Total de pares RBH (candidatos a ortólogos): {len(df)}")
print(df.head())

# e-values muito pequenos ficam mais legíveis em escala log
df["log_evalue_A_para_B"] = df["evalue_A_para_B"].apply(
    lambda x: -1 * np.log10(x) if x > 0 else 300
)

plt.figure(figsize=(8, 5))
plt.hist(df["log_evalue_A_para_B"], bins=30, color="#4C72B0", edgecolor="white")
plt.xlabel("-log10(e-value)  (quanto maior, mais forte a correspondência)")
plt.ylabel("Número de pares RBH")
plt.title("Distribuição da força das correspondências recíprocas (RBH)")
plt.tight_layout()
plt.savefig(os.path.join("results", "distribuicao_evalues.png"), dpi=150)
plt.show()

print("Gráfico salvo em results/distribuicao_evalues.png")