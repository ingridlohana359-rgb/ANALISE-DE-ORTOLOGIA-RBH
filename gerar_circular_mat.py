import numpy as np
import matplotlib.pyplot as plt
from Bio import Phylo
from pathlib import Path

RESULTS_DIR = Path.home() / "bioinformatica" / "resultados_pipeline"
TREE_FILE = RESULTS_DIR / "arvore_iqtree.treefile"
OUTPUT_PNG = RESULTS_DIR / "arvore_circular.png"

if TREE_FILE.exists():
    print("[+] Lendo a árvore...")
    tree = Phylo.read(TREE_FILE, "newick")
    
    print("[+] Calculando coordenadas circulares...")
    leaves = tree.get_terminals()
    n_leaves = len(leaves)
    
    # Atribui posições angulares para cada folha
    angles = np.linspace(0, 2 * np.pi, n_leaves, endpoint=False)
    coords = {}
    for i, leaf in enumerate(leaves):
        coords[leaf] = angles[i]
        
    def get_angle(clade):
        if clade in coords:
            return coords[clade]
        sub_angles = [get_angle(c) for c in clade.clades]
        coords[clade] = np.mean(sub_angles)
        return coords[clade]
        
    get_angle(tree.root)
    
    def get_depths(clade, current_depth=0):
        depths = {clade: current_depth}
        for child in clade.clades:
            b = child.branch_length if child.branch_length is not None else 1.0
            depths.update(get_depths(child, current_depth + b))
        return depths

    depths = get_depths(tree.root)
    
    fig, ax = plt.subplots(figsize=(16, 16), subplot_kw={'projection': 'polar'}, dpi=300)
    
    def plot_clade(clade):
        r_parent = depths[clade]
        theta_parent = coords[clade]
        
        for child in clade.clades:
            r_child = depths[child]
            theta_child = coords[child]
            
            # Linha radial para a criança
            ax.plot([theta_child, theta_child], [r_parent, r_child], color='#2c3e50', lw=0.4)
            # Arco conectando os irmãos
            t_arc = np.linspace(min(theta_parent, theta_child), max(theta_parent, theta_child), 20)
            ax.plot(t_arc, [r_parent]*len(t_arc), color='#2c3e50', lw=0.4)
            
            plot_clade(child)

    print("[+] Desenhando a árvore em projeção circular...")
    plot_clade(tree.root)
    
    ax.set_axis_off()
    plt.title("Árvore Filogenética Circular - IQ-TREE (5.897 sequências)", fontsize=14, pad=20)
    
    plt.savefig(OUTPUT_PNG, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"[✓] Imagem circular perfeita gerada em: {OUTPUT_PNG}")
else:
    print("[-] Arquivo .treefile não encontrado.")
