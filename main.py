import os
import sys
import json
import shutil
import threading
import subprocess
import tkinter as tk

from tkinter import ttk, filedialog, messagebox


# ---------------- ESTADO DO PROGRAMA ----------------

download_em_andamento = False


# ---------------- CAMINHOS ----------------

def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


def get_ffmpeg_path():
    # FFmpeg incluído no executável
    if getattr(sys, "frozen", False):
        caminho = os.path.join(sys._MEIPASS, "ffmpeg.exe")

        if os.path.isfile(caminho):
            return caminho

    # FFmpeg na pasta do projeto
    caminho_local = os.path.join(
        get_base_path(),
        "ffmpeg",
        "ffmpeg.exe"
    )

    if os.path.isfile(caminho_local):
        return caminho_local

    # FFmpeg instalado no sistema
    return shutil.which("ffmpeg")


def localizar_ytdlp():
    # Procura o executável yt-dlp no PATH
    caminho = shutil.which("yt-dlp")

    if caminho:
        return [caminho], False

    # Procura yt-dlp.exe ao lado do programa
    caminho_local = os.path.join(
        get_base_path(),
        "yt-dlp.exe"
    )

    if os.path.isfile(caminho_local):
        return [caminho_local], False

    # Durante o desenvolvimento, tenta usar o módulo Python
    if not getattr(sys, "frozen", False):
        return [sys.executable, "-m", "yt_dlp"], True

    return None, False


# ---------------- ATUALIZAÇÃO DO YT-DLP ----------------

def atualizar_ytdlp():
    if getattr(sys, "frozen", False):
        return False, (
            "A atualização automática não está disponível "
            "nesta versão empacotada do programa."
        )

    try:
        resultado = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "yt-dlp"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180
        )

        if resultado.returncode == 0:
            return True, "yt-dlp atualizado com sucesso."

        detalhe = (
            resultado.stderr.strip()
            or resultado.stdout.strip()
            or "Não foi possível atualizar o yt-dlp."
        )

        return False, detalhe

    except subprocess.TimeoutExpired:
        return False, "A atualização excedeu o tempo limite."

    except Exception as erro:
        return False, str(erro)


# ---------------- CONFIGURAÇÃO ----------------

def salvar_config(config):
    caminho = os.path.join(get_base_path(), "config.json")

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
        "default_quality": "1080p"
    }

    caminho = os.path.join(get_base_path(), "config.json")

    if not os.path.exists(caminho):
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(padrao, arquivo, indent=4)

        return padrao

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            config_lida = json.load(arquivo)

        # Mantém os valores padrão caso falte alguma chave
        padrao.update(config_lida)

        return padrao

    except (OSError, json.JSONDecodeError) as erro:
        print("Erro ao carregar configuração:", erro)
        return padrao


config = carregar_config()


# ---------------- INTERFACE ----------------

root = tk.Tk()
root.title("PyMediaDownloader")
root.geometry("500x520")
root.resizable(False, False)


# ---------------- FUNÇÕES AUXILIARES ----------------

def atualizar_status(texto, cor="blue"):
    def atualizar():
        status_label.config(
            text=texto,
            fg=cor,
            wraplength=450
        )

    root.after(0, atualizar)


def mostrar_erro(titulo, mensagem):
    root.after(
        0,
        lambda: messagebox.showerror(titulo, mensagem)
    )


def perguntar_atualizacao():
    """
    Exibe a pergunta na thread principal e devolve a resposta
    à thread que está executando o download.
    """
    evento = threading.Event()
    resposta = {"atualizar": False}

    def perguntar():
        try:
            resposta["atualizar"] = messagebox.askyesno(
                "Atualizar yt-dlp?",
                "O download encontrou um erro HTTP 403.\n\n"
                "Deseja atualizar o yt-dlp e tentar novamente?"
            )
        finally:
            evento.set()

    root.after(0, perguntar)
    evento.wait()

    return resposta["atualizar"]


# ---------------- QUALIDADE ----------------

def atualizar_qualidades(event=None):
    if variavel_tipo.get() == "MP3 (ÁUDIO)":
        dropdown_qualidade["values"] = [
            "320kbps (Alta)",
            "192kbps (Média)",
            "128kbps (Baixa)"
        ]

        variavel_qualidade.set("320kbps (Alta)")

    else:
        dropdown_qualidade["values"] = [
            "1440p",
            "1080p",
            "720p",
            "480p",
            "360p"
        ]

        variavel_qualidade.set("1080p")


# ---------------- PASTAS ----------------

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


# ---------------- DOWNLOAD ----------------

def baixar_video():
    global download_em_andamento

    if download_em_andamento:
        return

    link = input_link.get().strip()

    if not link:
        status_label.config(
            text="Informe um link válido.",
            fg="red"
        )
        return

    pasta = config["download_path"]
    tipo = variavel_tipo.get()
    qualidade = variavel_qualidade.get()

    # Só bloqueia novos downloads depois de validar o link
    download_em_andamento = True

    botao_baixar.config(state="disabled")

    def montar_comando(comando_base, ffmpeg_path):
        if tipo == "MP3 (ÁUDIO)":
            mapa_audio = {
                "320kbps (Alta)": ("320K", "320kbps"),
                "192kbps (Média)": ("192K", "192kbps"),
                "128kbps (Baixa)": ("128K", "128kbps")
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
            altura = qualidade.replace("p", "")
            tag = f"{altura}p"

            output = os.path.join(
                pasta,
                f"%(title)s [{tag}].%(ext)s"
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

            # Tentativas para falhas de download
            "--retries", "10",
            "--fragment-retries", "20",
            "--file-access-retries", "10",
            "--retry-sleep", "2",

            # Não aceita fragmentos indisponíveis como se estivessem completos
            "--abort-on-unavailable-fragments",

            # Oculta avisos e progresso do yt-dlp
            "--no-warnings",
            "--quiet",

            "-o", output,
            link
        ]

    def executar_download(comando):
        return subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1800
        )

    def processo():
        try:
            atualizar_status("Preparando download...", "blue")

            os.makedirs(pasta, exist_ok=True)

            ffmpeg_path = get_ffmpeg_path()

            if not ffmpeg_path:
                atualizar_status("FFmpeg não encontrado.", "red")

                mostrar_erro(
                    "FFmpeg não encontrado",
                    "Coloque ffmpeg.exe na pasta ffmpeg do projeto "
                    "ou instale o FFmpeg e adicione-o ao PATH."
                )

                return

            comando_base, executar_com_python = localizar_ytdlp()

            if not comando_base:
                atualizar_status("yt-dlp não encontrado.", "red")

                mostrar_erro(
                    "yt-dlp não encontrado",
                    "Instale o yt-dlp ou coloque yt-dlp.exe "
                    "na pasta do programa."
                )

                return

            comando = montar_comando(
                comando_base,
                ffmpeg_path
            )

            atualizar_status("Baixando...", "blue")

            resultado = executar_download(comando)

            mensagem_erro = (
                resultado.stderr + "\n" + resultado.stdout
            )

            # Pergunta se deve atualizar quando encontra HTTP 403
            erro_403 = (
                resultado.returncode != 0
                and re.search(
                    r"HTTP Error 403|HTTP 403",
                    mensagem_erro,
                    re.IGNORECASE
                )
            )

            if erro_403:
                atualizar_status(
                    "Download encontrou um problema.",
                    "orange"
                )

                deseja_atualizar = perguntar_atualizacao()

                if deseja_atualizar:
                    atualizar_status(
                        "Atualizando yt-dlp...",
                        "blue"
                    )

                    atualizado, detalhe = atualizar_ytdlp()

                    if atualizado:
                        atualizar_status(
                            "Atualização concluída. Tentando novamente...",
                            "blue"
                        )

                        # Reconstrói o comando e tenta apenas mais uma vez
                        resultado = executar_download(
                            montar_comando(
                                comando_base,
                                ffmpeg_path
                            )
                        )

                        mensagem_erro = (
                            resultado.stderr + "\n" + resultado.stdout
                        )

                    else:
                        print("Falha na atualização:")
                        print(detalhe)

                        atualizar_status(
                            "Não foi possível atualizar o yt-dlp.",
                            "red"
                        )

                        mostrar_erro(
                            "Falha na atualização",
                            detalhe[-1500:]
                        )

                        return

                else:
                    atualizar_status(
                        "Download não concluído.",
                        "gray"
                    )
                    return

            # Resultado final para todos os casos
            if resultado.returncode == 0:
                atualizar_status(
                    "Download concluído!",
                    "green"
                )

            else:
                print("Erro técnico no download:")
                print(mensagem_erro)

                atualizar_status(
                    "Não foi possível concluir o download.",
                    "red"
                )

        except subprocess.TimeoutExpired:
            print("O download ou a atualização excedeu o tempo limite.")

            atualizar_status(
                "O download demorou demais. Tente novamente.",
                "orange"
            )

        except Exception as erro:
            print("Erro inesperado:", repr(erro))

            atualizar_status(
                "Ocorreu um erro ao processar o download.",
                "red"
            )

        finally:
            def finalizar():
                global download_em_andamento

                download_em_andamento = False
                botao_baixar.config(state="normal")

            root.after(0, finalizar)

    threading.Thread(
        target=processo,
        daemon=True
    ).start()


# ---------------- ELEMENTOS DA INTERFACE ----------------

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

input_link = tk.Entry(root, width=45)
input_link.pack(padx=20, pady=5)

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
    values=["MP4 (VÍDEO)", "MP3 (ÁUDIO)"],
    state="readonly",
    width=42
)

dropdown_tipo.pack(padx=20, pady=5)
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
    values=["1440p", "1080p", "720p", "480p", "360p"],
    state="readonly",
    width=42
)

dropdown_qualidade.pack(padx=20, pady=5)

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
    wraplength=350
)

label_caminho.pack(anchor="w", padx=20)

tk.Button(
    root,
    text="Alterar Pasta",
    command=alterar_pasta
).pack(pady=5)

tk.Button(
    root,
    text="Pasta download",
    font=("Arial", 11, "bold"),
    bg="#A5960D",
    fg="white",
    width=15,
    command=abrir_pasta
).pack(pady=12)

botao_baixar = tk.Button(
    root,
    text="Baixar",
    font=("Arial", 11, "bold"),
    bg="#4CAF50",
    fg="white",
    width=15,
    command=baixar_video
)

botao_baixar.pack(pady=12)

root.mainloop()