import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Estilo visual acadêmico
sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(figsize=(10, 6))

# Carregar dados
df = pd.read_csv('results/pares_rbh.csv')

# Converter e-values para -log10
df['log_evalue'] = -np.log10(df['evalue_A_para_B'] + 1e-180)

# Plotar Histograma + Curva de Densidade
sns.histplot(
    df['log_evalue'], 
    kde=True, 
    color="#1b4965", 
    edgecolor="white", 
    linewidth=0.8,
    bins=35,
    ax=ax
)

# Rótulos e título
ax.set_title("Distribuição de Conservação de Ortólogos (Reciprocal Best Hits)", fontsize=14, fontweight='bold', pad=15, color="#0f2537")
ax.set_xlabel("Significância Estatística: -log10(E-value)", fontsize=12, labelpad=10)
ax.set_ylabel("Frequência de Pares de Genes", fontsize=12, labelpad=10)

# Anotação com métricas
total_pares = len(df)
ax.annotate(
    f"Total de Ortólogos RBH: {total_pares}\nConservação Forte (E < 1e-50): {sum(df['evalue_A_para_B'] < 1e-50)}", 
    xy=(0.55, 0.80), 
    xycoords='axes fraction',
    fontsize=10,
    bbox=dict(boxstyle="round,pad=0.6", fc="#f4f8fb", ec="#62b6cb", lw=1.2)
)

plt.tight_layout()
plt.savefig('results/grafico_ortologia_apresentacao.png', dpi=300)
print("✓ Gráfico de alta definição salvo em: results/grafico_ortologia_apresentacao.png")

