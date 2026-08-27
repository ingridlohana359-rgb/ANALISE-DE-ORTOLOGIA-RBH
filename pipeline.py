import os
import subprocess
import sys
from pathlib import Path
import matplotlib.pyplot as plt
from Bio import Phylo

GITHUB_REPO_URL = "https://github.com/ingridlohana359-rgb/ANALISE-DE-ORTOLOGIA-RBH"

BASE_DIR = Path.home() / "bioinformatica"
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "resultados_pipeline"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MERGED_FASTA = RESULTS_DIR / "sequencias_combinadas.fasta"
DATES_CSV = BASE_DIR / "datas_amostragem.csv"
ALIGNED_FASTA = RESULTS_DIR / "alinhamento_mafft.fasta"
IQTREE_PREFIX = RESULTS_DIR / "arvore_iqtree"
TREETIME_OUT = RESULTS_DIR / "treetime_results"
TREE_PNG = RESULTS_DIR / "arvore_filogenetica.png"

def run_cmd(command, desc):
    print(f"\n[+] {desc}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"[✓] {desc} concluído com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"[-] Erro ao executar: {desc}")
        sys.exit(1)

def gerar_imagem_arvore():
    tree_file = Path(f"{IQTREE_PREFIX}.treefile")
    if tree_file.exists():
        print(f"\n[+] Gerando imagem da árvore filogenética...")
        tree = Phylo.read(tree_file, "newick")
        fig = plt.figure(figsize=(12, 8), dpi=300)
        axes = fig.add_subplot(1, 1, 1)
        Phylo.draw(tree, do_show=False, axes=axes)
        plt.savefig(TREE_PNG, bbox_inches='tight')
        plt.close()
        print(f"[✓] Imagem salva em: {TREE_PNG}")

def main():
    print(f"Iniciando pipeline baseada no repositório: {GITHUB_REPO_URL}")
    
    fa_files = list(DATA_DIR.glob("*.faa"))
    if not fa_files:
        print(f"[-] Erro: Nenhum arquivo .faa encontrado em {DATA_DIR}")
        sys.exit(1)

    # Reutiliza o alinhamento que o MAFFT já gerou com sucesso
    if not ALIGNED_FASTA.exists():
        print(f"[+] Combinando arquivos FASTA da pasta data...")
        with open(MERGED_FASTA, "w") as outfile:
            for fpath in fa_files:
                with open(fpath, "r") as infile:
                    outfile.write(infile.read())
        
        cmd_mafft = f"mafft --auto --anysymbol {MERGED_FASTA} > {ALIGNED_FASTA}"
        run_cmd(cmd_mafft, "Alinhamento com MAFFT")
    else:
        print(f"[✓] Alinhamento MAFFT já encontrado em {ALIGNED_FASTA}.")

    if not DATES_CSV.exists():
        with open(DATES_CSV, "w") as f:
            f.write("name,date\nespecie_A,2020\nespecie_B,2022\n")

    tree_file = Path(f"{IQTREE_PREFIX}.treefile")
    if not tree_file.exists():
        iqtree_cmd_name = "iqtree2" if subprocess.run("which iqtree2", shell=True, capture_output=True).returncode == 0 else "iqtree"
        # Modelo JTT fixo e limitação de memória (-mem 2G) para rodar leve sem dar erro de RAM
        cmd_iqtree = f"{iqtree_cmd_name} -s {ALIGNED_FASTA} -m JTT -bb 1000 -mem 2G -pre {IQTREE_PREFIX}"
        run_cmd(cmd_iqtree, "Reconstrução Filogenética com IQ-TREE (Modo leve)")
    else:
        print(f"[✓] Árvore IQ-TREE já encontrada.")

    cmd_treetime = f"treetime --tree {tree_file} --aln {ALIGNED_FASTA} --dates {DATES_CSV} --outdir {TREETIME_OUT}"
    run_cmd(cmd_treetime, "Análise de Relógio Molecular com TreeTime")

    gerar_imagem_arvore()

    print(f"\n==================================================")
    print(f" Pipeline executada com sucesso!")
    print(f"==================================================")

if __name__ == "__main__":
    main()
