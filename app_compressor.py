import os
import asyncio
import subprocess
import flet as ft
from PIL import Image

EXTENSOES_VIDEO = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
EXTENSOES_IMAGEM = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}

def formatar_tamanho(bytes_tam):
    mb = bytes_tam / (1024 * 1024)
    return f"{mb:.2f} MB"

def main(page: ft.Page):
    page.title = "Soliun Compressor"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.window.width = 760
    page.window.height = 690
    page.window.min_width = 700
    page.window.min_height = 650
    page.padding = 0

    estado = {
        "arquivo_selecionado": "",
        "pasta_destino": "",
        "tipo_arquivo": None,  # 'video' ou 'imagem'
        "comprimindo": False
    }

    # --- CABEÇALHO ---
    cabecalho = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.COMPRESS_ROUNDED, color="#1DB954", size=28),
                        ft.Text("Soliun Compressor", size=20, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8
                ),
                ft.Text("Desenvolvido por Josias Ramos da Silva", size=11, italic=True, color="#757575")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.Padding.symmetric(horizontal=24, vertical=14),
        bgcolor="#181818",
        border=ft.Border.only(bottom=ft.BorderSide(1, "#282828"))
    )

    # --- CARD 1: SELEÇÃO E DIAGNÓSTICO DO ARQUIVO ---
    icone_tipo = ft.Icon(ft.Icons.INSERT_DRIVE_FILE_ROUNDED, color="#1DB954", size=38)
    lbl_nome_arq = ft.Text(
        "Nenhum arquivo selecionado",
        size=14,
        weight=ft.FontWeight.W_600,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS
    )
    lbl_info_arq = ft.Text(
        "Selecione um vídeo (MP4, MKV, MOV...) ou imagem (JPG, PNG, WEBP...)",
        size=12,
        color="#A0A0A0"
    )

    seletor_arquivo = ft.FilePicker()

    async def escolher_arquivo(e):
        arquivos = await seletor_arquivo.pick_files(
            dialog_title="Selecione um vídeo ou imagem",
            allow_multiple=False,
            allowed_extensions=["mp4", "mkv", "avi", "mov", "wmv", "webm", "jpg", "jpeg", "png", "webp", "bmp"]
        )
        if not arquivos:
            return

        caminho = arquivos[0].path
        ext = os.path.splitext(caminho)[1].lower()

        if ext in EXTENSOES_VIDEO:
            estado["tipo_arquivo"] = "video"
            icone_tipo.name = ft.Icons.VIDEO_FILE_ROUNDED
            tipo_label = "VÍDEO"
        elif ext in EXTENSOES_IMAGEM:
            estado["tipo_arquivo"] = "imagem"
            icone_tipo.name = ft.Icons.IMAGE_ROUNDED
            tipo_label = "IMAGEM"
        else:
            lbl_info_arq.value = "Formato não suportado."
            page.update()
            return

        estado["arquivo_selecionado"] = caminho
        tam_bytes = os.path.getsize(caminho)
        lbl_nome_arq.value = os.path.basename(caminho)
        lbl_info_arq.value = f"Tipo: {tipo_label}  •  Tamanho Original: {formatar_tamanho(tam_bytes)}"

        if not estado["pasta_destino"]:
            lbl_pasta.value = os.path.dirname(caminho)

        card_resultado.visible = False
        page.update()

    card_arquivo = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=icone_tipo,
                    bgcolor="#242424",
                    padding=12,
                    border_radius=10
                ),
                ft.Column(
                    [lbl_nome_arq, lbl_info_arq],
                    spacing=3,
                    expand=True
                ),
                ft.Button(
                    "Selecionar Arquivo",
                    icon=ft.Icons.UPLOAD_FILE_ROUNDED,
                    bgcolor="#1DB954",
                    color="#000000",
                    height=42,
                    style=ft.ButtonStyle(
                        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=escolher_arquivo
                )
            ],
            spacing=14
        ),
        bgcolor="#181818",
        padding=16,
        border_radius=12,
        border=ft.Border.all(1, "#282828")
    )

    # --- CARD 2: CONFIGURAÇÕES DE COMPACTAÇÃO ---
    dd_modo = ft.Dropdown(
        label="Nível de Compactação",
        value="Equilibrado (Ideal para WhatsApp - 720p)",
        options=[
            ft.dropdown.Option("Equilibrado (Ideal para WhatsApp - 720p)"),
            ft.dropdown.Option("Leve (Alta Qualidade / Mantém Resolução)"),
            ft.dropdown.Option("Forte (Arquivo Bem Leve - 480p)"),
            ft.dropdown.Option("Tamanho Alvo em MB (Definir manualmente)"),
        ],
        bgcolor="#242424",
        border_color="#333333",
        focused_border_color="#1DB954",
        border_radius=10,
        expand=True
    )

    campo_mb = ft.TextField(
        label="Tamanho Alvo (MB)",
        value="15",
        width=160,
        bgcolor="#242424",
        border_color="#333333",
        focused_border_color="#1DB954",
        border_radius=10,
        visible=False
    )

    def ao_mudar_modo(e):
        campo_mb.visible = "Tamanho Alvo" in dd_modo.value
        page.update()

    dd_modo.on_change = ao_mudar_modo

    lbl_pasta = ft.Text(
        "Mesma pasta do arquivo original",
        size=12,
        color="#B3B3B3",
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
        expand=True
    )

    seletor_pasta = ft.FilePicker()

    async def escolher_pasta(e):
        caminho = await seletor_pasta.get_directory_path()
        if caminho:
            estado["pasta_destino"] = caminho
            lbl_pasta.value = caminho
            page.update()

    card_config = ft.Container(
        content=ft.Column(
            [
                ft.Text("Perfil de Otimização", size=13, weight=ft.FontWeight.BOLD, color="#E0E0E0"),
                ft.Row([dd_modo, campo_mb], spacing=12),
                ft.Text("Pasta de Destino", size=13, weight=ft.FontWeight.BOLD, color="#E0E0E0"),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.FOLDER_ROUNDED, color="#1DB954", size=20),
                            lbl_pasta,
                            ft.TextButton(
                                "Alterar",
                                style=ft.ButtonStyle(color="#1DB954"),
                                on_click=escolher_pasta
                            )
                        ],
                        spacing=10
                    ),
                    bgcolor="#242424",
                    padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                    border_radius=10
                )
            ],
            spacing=12
        ),
        bgcolor="#181818",
        padding=18,
        border_radius=12,
        border=ft.Border.all(1, "#282828")
    )

    # --- CARD DE RESULTADO COMPARATIVO ---
    lbl_res_antes = ft.Text("0 MB", size=15, weight=ft.FontWeight.BOLD, color="#B3B3B3")
    lbl_res_depois = ft.Text("0 MB", size=15, weight=ft.FontWeight.BOLD, color="#1DB954")
    lbl_res_economia = ft.Text("-0%", size=15, weight=ft.FontWeight.BOLD, color="#1DB954")

    card_resultado = ft.Container(
        content=ft.Row(
            [
                ft.Column([ft.Text("ORIGINAL", size=10, color="#888888"), lbl_res_antes], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color="#1DB954"),
                ft.Column([ft.Text("COMPRIMIDO", size=10, color="#888888"), lbl_res_depois], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.VerticalDivider(color="#333333"),
                ft.Column([ft.Text("REDUÇÃO", size=10, color="#888888"), lbl_res_economia], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND
        ),
        bgcolor="#1E1E1E",
        padding=12,
        border_radius=10,
        border=ft.Border.all(1, "#1DB954"),
        visible=False
    )

    # --- PROGRESSO E BOTÃO PRINCIPAL ---
    barra_progresso = ft.ProgressBar(value=0, color="#1DB954", bgcolor="#282828", height=8, border_radius=4)
    lbl_status = ft.Text("Selecione um arquivo para começar", size=12, color="#A0A0A0")

    btn_comprimir = ft.Button(
        "COMPRIMIR AGORA",
        icon=ft.Icons.BOLT_ROUNDED,
        bgcolor="#1DB954",
        color="#000000",
        height=48,
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    def obter_duracao_video(caminho):
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", caminho
        ]
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags)
        return float(res.stdout.strip())

    def processar_video_sync(entrada, saida, modo, alvo_texto):
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        if "Leve" in modo:
            cmd = [
                "ffmpeg", "-y", "-i", entrada,
                "-c:v", "libx264", "-crf", "23", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", saida
            ]
        elif "Equilibrado" in modo:
            cmd = [
                "ffmpeg", "-y", "-i", entrada,
                "-vf", "scale='min(1280,iw)':-2",
                "-c:v", "libx264", "-crf", "27", "-preset", "medium",
                "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", saida
            ]
        elif "Forte" in modo:
            cmd = [
                "ffmpeg", "-y", "-i", entrada,
                "-vf", "scale='min(854,iw)':-2",
                "-c:v", "libx264", "-crf", "31", "-preset", "fast",
                "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", saida
            ]
        else:
            alvo_mb = float(alvo_texto.replace(",", "."))
            if alvo_mb <= 0:
                raise ValueError("Tamanho alvo deve ser maior que zero.")
            duracao = obter_duracao_video(entrada)
            bitrate_total = ((alvo_mb * 8192) / duracao) * 0.90
            bitrate_audio = 96
            bitrate_video = max(int(bitrate_total - bitrate_audio), 150)
            cmd = [
                "ffmpeg", "-y", "-i", entrada,
                "-vf", "scale='min(1280,iw)':-2",
                "-c:v", "libx264", "-b:v", f"{bitrate_video}k",
                "-maxrate", f"{int(bitrate_video * 1.2)}k",
                "-bufsize", f"{int(bitrate_video * 2)}k",
                "-preset", "medium",
                "-c:a", "aac", "-b:a", f"{bitrate_audio}k",
                "-movflags", "+faststart", saida
            ]

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags)
        if proc.returncode != 0:
            raise Exception("Erro durante a conversão no FFmpeg.")

    def processar_imagem_sync(entrada, saida, modo, alvo_texto):
        img = Image.open(entrada)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        largura, altura = img.size

        if "Leve" in modo:
            qualidade, max_lado = 85, max(largura, altura)
        elif "Equilibrado" in modo:
            qualidade, max_lado = 72, 1920
        elif "Forte" in modo:
            qualidade, max_lado = 50, 1280
        else:
            alvo_mb = float(alvo_texto.replace(",", "."))
            if alvo_mb <= 0:
                raise ValueError("Tamanho alvo deve ser maior que zero.")
            alvo_bytes = alvo_mb * 1024 * 1024
            for q in range(90, 10, -5):
                img.save(saida, "JPEG", optimize=True, quality=q)
                if os.path.getsize(saida) <= alvo_bytes:
                    return
            img.thumbnail((largura // 2, altura // 2), Image.Resampling.LANCZOS)
            img.save(saida, "JPEG", optimize=True, quality=40)
            return

        if max(largura, altura) > max_lado:
            img.thumbnail((max_lado, max_lado), Image.Resampling.LANCZOS)
        img.save(saida, "JPEG", optimize=True, quality=qualidade)

    async def executar_compressao_async():
        entrada = estado["arquivo_selecionado"]
        if not entrada:
            lbl_status.value = "Selecione um arquivo antes de comprimir."
            lbl_status.color = "#FF5252"
            page.update()
            return

        if estado["comprimindo"]:
            return

        estado["comprimindo"] = True
        btn_comprimir.disabled = True
        card_resultado.visible = False
        barra_progresso.value = None  # animação contínua
        lbl_status.color = "#A0A0A0"
        lbl_status.value = "Comprimindo arquivo... Aguarde."
        page.update()

        pasta_final = estado["pasta_destino"] if estado["pasta_destino"] else os.path.dirname(entrada)
        nome_base = os.path.splitext(os.path.basename(entrada))[0]
        ext_saida = ".mp4" if estado["tipo_arquivo"] == "video" else ".jpg"
        saida = os.path.join(pasta_final, f"{nome_base}_comprimido{ext_saida}")

        modo = dd_modo.value
        alvo_texto = campo_mb.value
        tam_antes = os.path.getsize(entrada)

        try:
            if estado["tipo_arquivo"] == "video":
                await asyncio.to_thread(processar_video_sync, entrada, saida, modo, alvo_texto)
            else:
                await asyncio.to_thread(processar_imagem_sync, entrada, saida, modo, alvo_texto)

            tam_depois = os.path.getsize(saida)
            economia = max(0, (1 - (tam_depois / tam_antes)) * 100)

            lbl_res_antes.value = formatar_tamanho(tam_antes)
            lbl_res_depois.value = formatar_tamanho(tam_depois)
            lbl_res_economia.value = f"-{economia:.1f}%"
            card_resultado.visible = True

            barra_progresso.value = 1.0
            lbl_status.value = f"Salvo como: {os.path.basename(saida)}"
            lbl_status.color = "#1DB954"

            snack = ft.SnackBar(
                content=ft.Text("Compressão concluída com sucesso!", color="#000000", weight=ft.FontWeight.BOLD),
                bgcolor="#1DB954"
            )
            page.overlay.append(snack)
            snack.open = True
        except Exception as erro:
            barra_progresso.value = 0
            lbl_status.value = f"Erro: {erro}"
            lbl_status.color = "#FF5252"
        finally:
            estado["comprimindo"] = False
            btn_comprimir.disabled = False
            page.update()

    btn_comprimir.on_click = lambda _: page.run_task(executar_compressao_async)

    card_acao = ft.Container(
        content=ft.Column(
            [
                lbl_status,
                barra_progresso,
                card_resultado,
                ft.Row([btn_comprimir], alignment=ft.MainAxisAlignment.CENTER)
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        ),
        bgcolor="#181818",
        padding=18,
        border_radius=12,
        border=ft.Border.all(1, "#282828")
    )

    page.add(
        ft.Column(
            [
                cabecalho,
                ft.Container(
                    content=ft.Column(
                        [
                            card_arquivo,
                            card_config,
                            card_acao
                        ],
                        spacing=14
                    ),
                    padding=20,
                    expand=True
                )
            ],
            spacing=0,
            expand=True
        )
    )

if __name__ == "__main__":
    ft.run(main)