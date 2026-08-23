"""
download_genomes.py

Baixa os arquivos de proteínas (.faa) de dois genomas bacterianos do NCBI,
usando o módulo Entrez do Biopython.

Como usar:
    python download_genomes.py

Antes de rodar:
    - Instale as dependências: pip install biopython
    - Preencha ENTREZ_EMAIL abaixo com um e-mail válido (o NCBI exige isso
      para identificar quem está usando a API).
    - Troque ACCESSION_A / ACCESSION_B pelos genomas que você quiser comparar.
      Você encontra o "accession" (algo como GCF_XXXXXXXXX.X) na página do
      genoma no NCBI (https://www.ncbi.nlm.nih.gov/datasets/genome/).
"""

from Bio import Entrez
import subprocess
import sys
import os

# ---------- CONFIGURAÇÃO: edite estas linhas ----------
ENTREZ_EMAIL = "seu-email@exemplo.com"  # obrigatório para o NCBI

# Exemplos de bactérias pequenas e bem estudadas, boas para começar:
#   Escherichia coli K-12:      GCF_000005845.2
#   Haemophilus influenzae:     GCF_000027305.1
#   Mycoplasma genitalium:      GCF_000027325.1  (genoma bem pequeno, rápido de testar)
ACCESSION_A = "GCF_000005845.2"  # espécie A (ex: E. coli)
ACCESSION_B = "GCF_000027305.1"  # espécie B (ex: H. influenzae)

OUTPUT_DIR = "data"
# --------------------------------------------------------

Entrez.email = ENTREZ_EMAIL


def baixar_proteinas_ncbi_datasets(accession: str, saida: str) -> None:
    """
    Usa a ferramenta de linha de comando 'datasets' do NCBI para baixar
    o conjunto de proteínas (.faa) de um genoma, a partir do seu accession.

    Essa abordagem é mais confiável que o Entrez para pegar TODAS as
    proteínas de um genoma de uma vez (o Entrez é melhor para buscas
    pontuais de sequências específicas).
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Baixando genoma {accession}...")
    subprocess.run(
        [
            "datasets", "download", "genome", "accession", accession,
            "--include", "protein",
            "--filename", f"{accession}.zip",
        ],
        check=True,
    )

    # o NCBI Datasets baixa um .zip; extraímos e pegamos o protein.faa de dentro
    subprocess.run(["unzip", "-o", f"{accession}.zip", "-d", accession], check=True)

    caminho_proteina = os.path.join(
        accession, "ncbi_dataset", "data", accession, "protein.faa"
    )
    destino = os.path.join(OUTPUT_DIR, saida)
    subprocess.run(["cp", caminho_proteina, destino], check=True)
    print(f"Salvo em {destino}")


if __name__ == "__main__":
    try:
        baixar_proteinas_ncbi_datasets(ACCESSION_A, "especie_A.faa")
        baixar_proteinas_ncbi_datasets(ACCESSION_B, "especie_B.faa")
    except FileNotFoundError:
        print(
            "\nErro: o comando 'datasets' não foi encontrado.\n"
            "Instale o NCBI Datasets CLI antes de rodar este script:\n"
            "  https://www.ncbi.nlm.nih.gov/datasets/docs/v2/download-and-install/\n"
        )
        sys.exit(1)

    print("\nDownload concluído. Arquivos em:", OUTPUT_DIR)