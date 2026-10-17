import os
import sys
import json
import shutil
import queue
import threading
import subprocess
import tkinter as tk

from tkinter import ttk, filedialog, messagebox


# =====================================================
# CONFIGURAÇÕES
# =====================================================

MAX_DOWNLOADS_SIMULTANEOS = 3

fila_downloads = queue.Queue()
downloads = {}
contador_downloads = 0

lock_downloads = threading.Lock()
lock_atualizacao = threading.Lock()

janela_fila = None
tabela_downloads = None


# =====================================================
# CAMINHOS
# =====================================================

def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


def get_ffmpeg_path():
    if getattr(sys, "frozen", False):
        caminho = os.path.join(sys._MEIPASS, "ffmpeg.exe")

        if os.path.isfile(caminho):
            return caminho

    caminho_local = os.path.join(
        get_base_path(),
        "ffmpeg",
        "ffmpeg.exe"
    )

    if os.path.isfile(caminho_local):
        return caminho_local

    return shutil.which("ffmpeg")


def localizar_ytdlp():
    caminho = shutil.which("yt-dlp")

    if caminho:
        return [caminho]

    caminho_local = os.path.join(
        get_base_path(),
        "yt-dlp.exe"
    )

    if os.path.isfile(caminho_local):
        return [caminho_local]

    if not getattr(sys, "frozen", False):
        return [sys.executable, "-m", "yt_dlp"]

    return None


# =====================================================
# CONFIGURAÇÃO DO PROGRAMA
# =====================================================

def salvar_config(config):
    caminho = os.path.join(
        get_base_path(),
        "config.json"
    )

    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(config, arquivo, indent=4)

    except Exception as erro:
        print("Erro ao salvar configuração:", erro)


def carregar_config():
    padrao = {
        "download_path": os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        ),
        "default_type": "MP4 (VÍDEO)",
        "default_quality": "1080p (Full HD)"
    }

    caminho = os.path.join(
        get_base_path(),
        "config.json"
    )

    if not os.path.exists(caminho):
        salvar_config(padrao)
        return padrao

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            config_lida = json.load(arquivo)

        padrao.update(config_lida)

        return padrao

    except (OSError, json.JSONDecodeError) as erro:
        print("Erro ao carregar configuração:", erro)
        return padrao


config = carregar_config()


# =====================================================
# INTERFACE PRINCIPAL
# =====================================================

root = tk.Tk()
root.title("PyMediaDownloader")
root.geometry("500x570")
root.resizable(False, False)


# =====================================================
# ATUALIZAÇÃO DA INTERFACE
# =====================================================

def atualizar_status_geral(texto, cor="blue"):
    root.after(
        0,
        lambda: status_label.config(
            text=texto,
            fg=cor
        )
    )


def atualizar_item(id_download, **alteracoes):
    """
    Atualiza os dados de um download e sua linha na tabela.
    """

    def atualizar():
        with lock_downloads:
            if id_download not in downloads:
                return

            downloads[id_download].update(alteracoes)

            dados = downloads[id_download].copy()

        if tabela_downloads is not None:
            if tabela_downloads.exists(str(id_download)):
                tabela_downloads.item(
                    str(id_download),
                    values=(
                        dados["titulo"],
                        dados["tipo"],
                        dados["qualidade"],
                        dados["status"]
                    )
                )

    root.after(0, atualizar)


def atualizar_contador():
    with lock_downloads:
        aguardando = sum(
            1 for item in downloads.values()
            if item["status"] == "Aguardando"
        )

        baixando = sum(
            1 for item in downloads.values()
            if item["status"] == "Baixando"
        )

    atualizar_status_geral(
        f"Na fila: {aguardando} | Baixando: {baixando}",
        "blue"
    )


# =====================================================
# QUALIDADES
# =====================================================

def atualizar_qualidades(event=None):
    if variavel_tipo.get() == "MP3 (ÁUDIO)":
        dropdown_qualidade["values"] = [
            "48kbps (Baixa)",
            "128kbps (Normal)",
            "192kbps (Alta)",
            "256kbps (Premium)"
        ]

        variavel_qualidade.set("128kbps (Normal)")

    else:
        dropdown_qualidade["values"] = [
            "4320p (8K)",
            "2160p (4K)",
            "1440p (2K)",
            "1080p (Full HD)",
            "720p (HD)",
            "480p (SD)",
            "360p (SD)",
            "240p (SD)",
            "144p"
        ]

        variavel_qualidade.set("1080p (Full HD)")


# =====================================================
# PASTAS
# =====================================================

def alterar_pasta():
    pasta = filedialog.askdirectory(
        initialdir=config.get("download_path", "")
    )

    if pasta:
        config["download_path"] = pasta
        salvar_config(config)

        label_caminho.config(text=pasta)


def abrir_pasta():
    pasta = config.get("download_path")

    if pasta and os.path.isdir(pasta):
        try:
            os.startfile(pasta)

        except OSError as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir a pasta.\n{erro}"
            )

    else:
        messagebox.showerror(
            "Pasta inválida",
            "A pasta de downloads não existe."
        )


# =====================================================
# JANELA DA FILA DE DOWNLOADS
# =====================================================

def abrir_lista_downloads():
    global janela_fila, tabela_downloads

    if janela_fila is not None:
        try:
            if janela_fila.winfo_exists():
                janela_fila.lift()
                janela_fila.focus_force()
                return
        except tk.TclError:
            pass

    janela_fila = tk.Toplevel(root)
    janela_fila.title("Lista de downloads")
    janela_fila.geometry("760x430")
    janela_fila.minsize(650, 350)

    # Botão X da janela
    janela_fila.protocol(
        "WM_DELETE_WINDOW",
        fechar_lista_downloads
    )

    tk.Label(
        janela_fila,
        text="Lista de downloads",
        font=("Arial", 15, "bold")
    ).pack(pady=12)

    frame_tabela = tk.Frame(janela_fila)
    frame_tabela.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=5
    )

    colunas = (
        "titulo",
        "tipo",
        "qualidade",
        "status"
    )

    tabela_downloads = ttk.Treeview(
        frame_tabela,
        columns=colunas,
        show="headings",
        selectmode="extended"
    )

    tabela_downloads.heading("titulo", text="Download")
    tabela_downloads.heading("tipo", text="Tipo")
    tabela_downloads.heading("qualidade", text="Qualidade")
    tabela_downloads.heading("status", text="Status")

    tabela_downloads.column(
        "titulo",
        width=300,
        minwidth=180
    )

    tabela_downloads.column(
        "tipo",
        width=100,
        anchor="center"
    )

    tabela_downloads.column(
        "qualidade",
        width=130,
        anchor="center"
    )

    tabela_downloads.column(
        "status",
        width=140,
        anchor="center"
    )

    barra_vertical = ttk.Scrollbar(
        frame_tabela,
        orient="vertical",
        command=tabela_downloads.yview
    )

    tabela_downloads.configure(
        yscrollcommand=barra_vertical.set
    )

    tabela_downloads.pack(
        side="left",
        fill="both",
        expand=True
    )

    barra_vertical.pack(
        side="right",
        fill="y"
    )

    # Carrega os downloads existentes
    with lock_downloads:
        itens = list(downloads.items())

    for id_download, dados in itens:
        tabela_downloads.insert(
            "",
            "end",
            iid=str(id_download),
            values=(
                dados["titulo"],
                dados["tipo"],
                dados["qualidade"],
                dados["status"]
            )
        )

    frame_botoes = tk.Frame(janela_fila)
    frame_botoes.pack(pady=12)

    tk.Button(
        frame_botoes,
        text="Remover selecionados",
        command=remover_downloads_selecionados
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botoes,
        text="Limpar concluídos",
        command=limpar_concluidos
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botoes,
        text="Voltar",
        width=12,
        command=fechar_lista_downloads
    ).pack(side="left", padx=5)


def fechar_lista_downloads():
    global janela_fila, tabela_downloads

    if janela_fila is not None:
        try:
            janela_fila.destroy()
        except tk.TclError:
            pass

    janela_fila = None
    tabela_downloads = None


def remover_downloads_selecionados():
    if tabela_downloads is None:
        return

    selecionados = tabela_downloads.selection()

    if not selecionados:
        return

    removidos = 0

    for item_id in selecionados:
        id_download = int(item_id)

        with lock_downloads:
            dados = downloads.get(id_download)

            if dados is None:
                continue

            # Só remove downloads que ainda não começaram
            if dados["status"] != "Aguardando":
                continue

            dados["status"] = "Removido"
            removidos += 1

        tabela_downloads.delete(item_id)

    if removidos:
        atualizar_contador()


def limpar_concluidos():
    if tabela_downloads is None:
        return

    with lock_downloads:
        ids = [
            id_download
            for id_download, dados in downloads.items()
            if dados["status"] in (
                "Concluído",
                "Erro",
                "Removido"
            )
        ]

        for id_download in ids:
            downloads.pop(id_download, None)

    for item_id in tabela_downloads.get_children():
        if int(item_id) in ids:
            tabela_downloads.delete(item_id)

    atualizar_contador()


# =====================================================
# MONTAGEM DO COMANDO
# =====================================================

def montar_comando(download):
    comando_base = localizar_ytdlp()

    if not comando_base:
        raise FileNotFoundError(
            "O yt-dlp não foi encontrado."
        )

    ffmpeg_path = get_ffmpeg_path()

    if not ffmpeg_path:
        raise FileNotFoundError(
            "O FFmpeg não foi encontrado."
        )

    pasta = download["pasta"]
    tipo = download["tipo"]
    qualidade = download["qualidade"]
    link = download["link"]

    if tipo == "MP3 (ÁUDIO)":
        mapa_audio = {
            "48kbps (Baixa)": ("48K", "48kbps"),
            "128kbps (Normal)": ("128K", "128kbps"),
            "192kbps (Alta)": ("192K", "192kbps"),
            "256kbps (Premium)": ("256K", "256kbps")
        }

        bitrate, tag = mapa_audio[qualidade]

        output = os.path.join(
            pasta,
            f"%(title)s [{tag}].%(ext)s"
        )

        argumentos = [
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", bitrate
        ]

    else:
        mapa_video = {
            "4320p (8K)": 4320,
            "2160p (4K)": 2160,
            "1440p (2K)": 1440,
            "1080p (Full HD)": 1080,
            "720p (HD)": 720,
            "480p (SD)": 480,
            "360p (SD)": 360,
            "240p (SD)": 240,
            "144p": 144
        }

        altura = mapa_video[qualidade]

        output = os.path.join(
            pasta,
            f"%(title)s [{altura}p].%(ext)s"
        )

        formato = (
            f"bestvideo[ext=mp4][height<={altura}]"
            f"+bestaudio[ext=m4a]/best[ext=mp4]/best"
        )

        argumentos = [
            "-f", formato,
            "--merge-output-format", "mp4"
        ]

    return comando_base + [
        *argumentos,

        "--ffmpeg-location", ffmpeg_path,
        "--no-overwrites",

        "--retries", "10",
        "--fragment-retries", "20",
        "--file-access-retries", "10",
        "--retry-sleep", "2",

        "--abort-on-unavailable-fragments",

        "--no-warnings",
        "--quiet",

        "-o", output,
        link
    ]


# =====================================================
# EXECUÇÃO INDIVIDUAL DO DOWNLOAD
# =====================================================

def executar_download(id_download, download):
    try:
        atualizar_item(
            id_download,
            status="Baixando"
        )

        atualizar_contador()

        os.makedirs(
            download["pasta"],
            exist_ok=True
        )

        comando = montar_comando(download)

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1800
        )

        if resultado.returncode == 0:
            atualizar_item(
                id_download,
                status="Concluído"
            )

        else:
            mensagem = (
                resultado.stderr
                + "\n"
                + resultado.stdout
            )

            print(
                f"\nErro no download {id_download}:"
            )
            print(mensagem)

            atualizar_item(
                id_download,
                status="Erro"
            )

    except subprocess.TimeoutExpired:
        print(
            f"Download {id_download}: tempo limite excedido."
        )

        atualizar_item(
            id_download,
            status="Erro"
        )

    except Exception as erro:
        print(
            f"Erro no download {id_download}: {erro}"
        )

        atualizar_item(
            id_download,
            status="Erro"
        )

    finally:
        atualizar_contador()
        


# =====================================================
# TRABALHADORES DA FILA
# =====================================================

def trabalhador():
    while True:
        tarefa = fila_downloads.get()

        try:
            if tarefa is None:
                return

            id_download, download = tarefa

            with lock_downloads:
                dados = downloads.get(id_download)

                if (
                    dados is None
                    or dados["status"] == "Removido"
                ):
                    continue

            executar_download(
                id_download,
                download
            )

        finally:
            if tarefa is not None:
                fila_downloads.task_done()


def iniciar_trabalhadores():
    for _ in range(MAX_DOWNLOADS_SIMULTANEOS):
        thread = threading.Thread(
            target=trabalhador,
            daemon=True
        )

        thread.start()


# =====================================================
# ADICIONAR DOWNLOAD À FILA
# =====================================================

def adicionar_download():
    global contador_downloads

    link = input_link.get().strip()

    if not link:
        status_label.config(
            text="Informe um link válido.",
            fg="red"
        )
        return

    tipo = variavel_tipo.get()
    qualidade = variavel_qualidade.get()
    pasta = config["download_path"]

    contador_downloads += 1
    id_download = contador_downloads

    # Cada tarefa guarda suas próprias configurações
    download = {
        "link": link,
        "tipo": tipo,
        "qualidade": qualidade,
        "pasta": pasta
    }

    dados = {
        "titulo": f"Download {id_download}",
        "tipo": "MP3" if tipo == "MP3 (ÁUDIO)" else "MP4",
        "qualidade": qualidade,
        "status": "Aguardando"
    }

    with lock_downloads:
        downloads[id_download] = dados

    fila_downloads.put(
        (id_download, download)
    )

    # Limpa o campo após adicionar
    input_link.delete(0, tk.END)

    status_label.config(
        text=f"Download {id_download} adicionado à fila.",
        fg="green"
    )

    # Atualiza a janela da fila, se estiver aberta
    if (
        tabela_downloads is not None
        and janela_fila is not None
        and janela_fila.winfo_exists()
    ):
        tabela_downloads.insert(
            "",
            "end",
            iid=str(id_download),
            values=(
                dados["titulo"],
                dados["tipo"],
                dados["qualidade"],
                dados["status"]
            )
        )

    atualizar_contador()


# =====================================================
# INTERFACE PRINCIPAL
# =====================================================

tk.Label(
    root,
    text="PyMediaDownloader",
    font=("Arial", 16, "bold")
).pack(pady=10)

tk.Label(
    root,
    text="Link:",
    font=("Arial", 10, "bold")
).pack(anchor="w", padx=20)

input_link = tk.Entry(
    root,
    width=45
)

input_link.pack(
    padx=20,
    pady=5
)

tk.Label(
    root,
    text="Tipo:",
    font=("Arial", 10, "bold")
).pack(anchor="w", padx=20)

variavel_tipo = tk.StringVar(
    value=config["default_type"]
)

dropdown_tipo = ttk.Combobox(
    root,
    textvariable=variavel_tipo,
    values=[
        "MP4 (VÍDEO)",
        "MP3 (ÁUDIO)"
    ],
    state="readonly",
    width=42
)

dropdown_tipo.pack(
    padx=20,
    pady=5
)

dropdown_tipo.bind(
    "<<ComboboxSelected>>",
    atualizar_qualidades
)

tk.Label(
    root,
    text="Qualidade:",
    font=("Arial", 10, "bold")
).pack(anchor="w", padx=20)

variavel_qualidade = tk.StringVar(
    value=config["default_quality"]
)

dropdown_qualidade = ttk.Combobox(
    root,
    textvariable=variavel_qualidade,
    values=[
        "4320p (8K)",
        "2160p (4K)",
        "1440p (2K)",
        "1080p (Full HD)",
        "720p (HD)",
        "480p (SD)",
        "360p (SD)",
        "240p (SD)",
        "144p"
    ],
    state="readonly",
    width=42
)

dropdown_qualidade.pack(
    padx=20,
    pady=5
)

status_label = tk.Label(
    root,
    text="Pronto",
    fg="gray",
    wraplength=450
)

status_label.pack(pady=8)

tk.Label(
    root,
    text="Local do download:",
    font=("Arial", 10, "bold")
).pack(anchor="w", padx=20)

label_caminho = tk.Label(
    root,
    text=config["download_path"],
    wraplength=430
)

label_caminho.pack(
    anchor="w",
    padx=20
)

tk.Button(
    root,
    text="Alterar Pasta",
    command=alterar_pasta
).pack(pady=5)

tk.Button(
    root,
    text="Pasta download",
    font=("Arial", 10, "bold"),
    bg="#A5960D",
    fg="white",
    width=20,
    command=abrir_pasta
).pack(pady=6)

tk.Button(
    root,
    text="Adicionar à fila",
    font=("Arial", 11, "bold"),
    bg="#4CAF50",
    fg="white",
    width=20,
    command=adicionar_download
).pack(pady=6)

tk.Button(
    root,
    text="Lista de downloads",
    font=("Arial", 11, "bold"),
    width=20,
    command=abrir_lista_downloads
).pack(pady=6)


# =====================================================
# INICIALIZAÇÃO
# =====================================================

iniciar_trabalhadores()

root.mainloop()