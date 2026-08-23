"""
reciprocal_best_hits.py

Implementa o método "tree-free" de Reciprocal Best Hit (RBH) para encontrar
pares de genes candidatos a ortólogos entre duas espécies bacterianas,
comparando sequências de proteínas diretamente — sem construir nenhuma
árvore filogenética.

A lógica (a mesma discutida no capítulo do livro):
    1. Para cada proteína da espécie A, encontramos sua melhor
       correspondência (menor e-value) na espécie B.
    2. Para cada proteína da espécie B, fazemos o caminho inverso: achamos
       sua melhor correspondência na espécie A.
    3. Se a proteína A1 aponta para B1 como melhor hit, E a proteína B1
       aponta de volta para A1, esse par é uma "melhor correspondência
       recíproca" (RBH) — um forte candidato a par de genes ortólogos.

Pré-requisitos:
    - BLAST+ instalado:  sudo apt install ncbi-blast+
    - Biopython:         pip install biopython
    - Os arquivos data/especie_A.faa e data/especie_B.faa já baixados
      (rode download_genomes.py primeiro).

Como usar:
    python reciprocal_best_hits.py
"""

import subprocess
import os
import csv
from Bio import SeqIO
from Bio.Blast import NCBIXML

DATA_DIR = "data"
RESULTS_DIR = "results"

FASTA_A = os.path.join(DATA_DIR, "especie_A.faa")
FASTA_B = os.path.join(DATA_DIR, "especie_B.faa")

# limiar de e-value: quanto menor, mais rigorosa é a exigência de
# similaridade para considerar um "hit" válido
EVALUE_LIMIAR = 1e-5


def criar_banco_blast(fasta: str, nome_banco: str) -> None:
    """Transforma um arquivo FASTA em um banco de dados pesquisável pelo BLAST."""
    subprocess.run(
        ["makeblastdb", "-in", fasta, "-dbtype", "prot", "-out", nome_banco],
        check=True,
    )


def rodar_blastp(fasta_consulta: str, banco: str, saida_xml: str) -> None:
    """Roda blastp comparando cada sequência de fasta_consulta contra o banco."""
    subprocess.run(
        [
            "blastp",
            "-query", fasta_consulta,
            "-db", banco,
            "-out", saida_xml,
            "-outfmt", "5",       # formato XML, mais fácil de parsear
            "-evalue", str(EVALUE_LIMIAR),
            "-max_target_seqs", "1",  # só nos interessa o melhor hit
        ],
        check=True,
    )


def melhores_hits(caminho_xml: str) -> dict:
    """
    Lê um resultado de BLAST em XML e retorna um dicionário:
        { id_da_sequencia_consulta: id_do_melhor_hit }
    considerando apenas o alinhamento de menor e-value para cada consulta.
    """
    melhores = {}
    with open(caminho_xml) as handle:
        for registro in NCBIXML.parse(handle):
            if not registro.alignments:
                continue  # essa proteína não teve nenhum hit significativo

            query_id = registro.query.split()[0]

            melhor_alinhamento = registro.alignments[0]
            melhor_hsp = melhor_alinhamento.hsps[0]

            # garante que estamos pegando o alinhamento de menor e-value,
            # caso a lista não venha ordenada
            for alinhamento in registro.alignments:
                for hsp in alinhamento.hsps:
                    if hsp.expect < melhor_hsp.expect:
                        melhor_hsp = hsp
                        melhor_alinhamento = alinhamento

            hit_id = melhor_alinhamento.hit_def.split()[0]
            melhores[query_id] = (hit_id, melhor_hsp.expect)

    return melhores


def encontrar_pares_rbh(hits_a_para_b: dict, hits_b_para_a: dict) -> list:
    """
    Cruza os dois dicionários de melhores hits e retorna a lista de pares
    que são recíprocos: A -> B e B -> A apontam um para o outro.
    """
    pares_rbh = []
    for gene_a, (gene_b, evalue_ab) in hits_a_para_b.items():
        if gene_b in hits_b_para_a:
            gene_a_volta, evalue_ba = hits_b_para_a[gene_b]
            if gene_a_volta == gene_a:
                pares_rbh.append((gene_a, gene_b, evalue_ab, evalue_ba))
    return pares_rbh


def salvar_csv(pares: list, caminho_saida: str) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(caminho_saida, "w", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["gene_especie_A", "gene_especie_B", "evalue_A_para_B", "evalue_B_para_A"])
        escritor.writerows(pares)
    print(f"{len(pares)} pares RBH salvos em {caminho_saida}")


if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("1. Criando bancos de dados BLAST...")
    criar_banco_blast(FASTA_A, os.path.join(RESULTS_DIR, "banco_A"))
    criar_banco_blast(FASTA_B, os.path.join(RESULTS_DIR, "banco_B"))

    print("2. Rodando BLAST: A contra B...")
    rodar_blastp(FASTA_A, os.path.join(RESULTS_DIR, "banco_B"), os.path.join(RESULTS_DIR, "A_vs_B.xml"))

    print("3. Rodando BLAST: B contra A...")
    rodar_blastp(FASTA_B, os.path.join(RESULTS_DIR, "banco_A"), os.path.join(RESULTS_DIR, "B_vs_A.xml"))

    print("4. Extraindo melhores hits de cada sentido...")
    hits_a_para_b = melhores_hits(os.path.join(RESULTS_DIR, "A_vs_B.xml"))
    hits_b_para_a = melhores_hits(os.path.join(RESULTS_DIR, "B_vs_A.xml"))

    print("5. Cruzando os resultados para achar pares recíprocos (RBH)...")
    pares_rbh = encontrar_pares_rbh(hits_a_para_b, hits_b_para_a)

    salvar_csv(pares_rbh, os.path.join(RESULTS_DIR, "pares_rbh.csv"))