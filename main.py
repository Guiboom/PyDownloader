import os
import json
import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import threading
import sys


# ---------------- FFmpeg PATH ----------------
def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "ffmpeg.exe")
    else:
        return os.path.join("ffmpeg", "ffmpeg.exe")


ffmpeg_path = get_ffmpeg_path()


# ---------------- CONFIG ----------------
def salvar_config(config):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def carregar_config():
    padrao = {
        "download_path": "Downloads",
        "default_type": "MP4 (VÍDEO)",
        "default_quality": "1080p"
    }

    if not os.path.exists("config.json"):
        salvar_config(padrao)
        return padrao

    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


config = carregar_config()


# ---------------- UI ----------------
root = tk.Tk()
root.title("PyMediaDownloader")
root.geometry("500x520")
root.resizable(False, False)


# ---------------- FUNÇÕES ----------------
def atualizar_qualidades(event=None):
    if variavel_tipo.get() == "MP3 (ÁUDIO)":
        dropdown_qualidade["values"] = ["320kbps (Alta)", "192kbps (Média)", "128kbps (Baixa)"]
        variavel_qualidade.set("320kbps (Alta)")
    else:
        dropdown_qualidade["values"] = ["1080p", "720p", "480p", "360p"]
        variavel_qualidade.set("1080p")


def alterar_pasta():
    pasta = filedialog.askdirectory()
    if pasta:
        config["download_path"] = pasta
        salvar_config(config)
        label_caminho.config(text=pasta)


def baixar_video():
    link = input_link.get().strip()

    if not link:
        status_label.config(text="❌ Link inválido", fg="red")
        return

    pasta = config["download_path"]
    tipo = variavel_tipo.get()
    qualidade = variavel_qualidade.get()

    def processo():
        try:
            root.after(0, lambda: status_label.config(text="⏳ Baixando...", fg="blue"))

            # ---------------- AUDIO ----------------
            if tipo == "MP3 (ÁUDIO)":

                mapa_audio = {
                    "320kbps (Alta)": ("320K", "320kbps"),
                    "192kbps (Média)": ("192K", "192kbps"),
                    "128kbps (Baixa)": ("128K", "128kbps"),
                }

                bitrate, tag = mapa_audio[qualidade]

                output = os.path.join(pasta, f"%(title)s [{tag}].%(ext)s")

                comando = [
                    "yt-dlp",
                    "-x",
                    "--audio-format", "mp3",
                    "--audio-quality", bitrate,
                    "--ffmpeg-location", ffmpeg_path,
                    "--no-overwrites",
                    "-o", output,
                    link
                ]

            # ---------------- VIDEO ----------------
            else:
                height = qualidade.replace("p", "")
                tag = f"{height}p"

                output = os.path.join(pasta, f"%(title)s [{tag}].%(ext)s")

                fmt = (
                    f"bestvideo[ext=mp4][height<={height}]"
                    f"+bestaudio[ext=m4a]/best[ext=mp4]/best"
                )

                comando = [
                    "yt-dlp",
                    "-f", fmt,
                    "--merge-output-format", "mp4",
                    "--ffmpeg-location", ffmpeg_path,
                    "--no-overwrites",
                    "-o", output,
                    link
                ]

            result = subprocess.run(comando, capture_output=True, text=True)

            if result.returncode == 0:
                root.after(0, lambda: status_label.config(text="✅ Download concluído!", fg="green"))
            else:
                root.after(0, lambda: status_label.config(text="❌ Erro no download", fg="red"))

        except Exception as e:
            root.after(0, lambda: status_label.config(text=f"❌ Erro: {e}", fg="red"))

    threading.Thread(target=processo, daemon=True).start()


# ---------------- UI ELEMENTOS ----------------
tk.Label(root, text="PyMediaDownloader", font=("Arial", 16, "bold")).pack(pady=10)

tk.Label(root, text="Link:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20)
input_link = tk.Entry(root, width=45)
input_link.pack(padx=20, pady=5)

tk.Label(root, text="Tipo:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20)

variavel_tipo = tk.StringVar(value=config["default_type"])
dropdown_tipo = ttk.Combobox(
    root,
    textvariable=variavel_tipo,
    values=["MP4 (VÍDEO)", "MP3 (ÁUDIO)"],
    state="readonly",
    width=42
)
dropdown_tipo.pack(padx=20, pady=5)
dropdown_tipo.bind("<<ComboboxSelected>>", atualizar_qualidades)

tk.Label(root, text="Qualidade:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20)

variavel_qualidade = tk.StringVar(value=config["default_quality"])
dropdown_qualidade = ttk.Combobox(
    root,
    textvariable=variavel_qualidade,
    values=["1080p", "720p", "480p", "360p"],
    state="readonly",
    width=42
)
dropdown_qualidade.pack(padx=20, pady=5)

status_label = tk.Label(root, text="Pronto", fg="gray")
status_label.pack(pady=8)

tk.Label(root, text="Local do download:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20)

label_caminho = tk.Label(root, text=config["download_path"], wraplength=350)
label_caminho.pack(anchor="w", padx=20)

tk.Button(root, text="Alterar Pasta", command=alterar_pasta).pack(pady=5)

tk.Button(
    root,
    text="Baixar",
    font=("Arial", 11, "bold"),
    bg="#4CAF50",
    fg="white",
    width=15,
    command=baixar_video
).pack(pady=12)

root.mainloop()