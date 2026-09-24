import os
import subprocess

pasta_projeto = "." 
# Nome exato do arquivo da sua árvore na pasta
arquivo_arvore = "arvore_filogenetica_super_resolucao.png"

caminho_completo = os.path.join(pasta_projeto, arquivo_arvore)

if not os.path.exists(caminho_completo):
    print(f"Erro: O arquivo {arquivo_arvore} não foi encontrado na pasta.")
else:
    print(f"Árvore encontrada! Gerando o vídeo para o Story...")

    output_video = "story_bioinformatica.mp4"

    # Comando do FFmpeg otimizado para formato vertical 9:16 (1080x1920)
    # Deixa a imagem aparecendo por 5 segundos
    comando = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", caminho_completo,
        "-t", "5",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        os.path.join(pasta_projeto, output_video)
    ]

    try:
        subprocess.run(comando, check=True)
        print(f"\n✨ Sucesso! Vídeo gerado com o nome: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o FFmpeg: {e}")
