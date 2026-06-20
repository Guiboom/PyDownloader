# PyMediaDownloader

Aplicativo prático para download de vídeos e áudios, com interface gráfica desenvolvida inteiramente em Python.

---

## 📌 Sobre o Projeto

O PyMediaDownloader foi criado como um projeto de aprendizado para explorar o desenvolvimento de interfaces gráficas em Python. Foi minha primeira experiência criando uma aplicação com interface visual, saindo dos programas executados apenas pelo terminal.

O projeto utiliza o poderoso `yt-dlp` no backend para realizar os downloads, oferecendo uma experiência simples e amigável para o usuário final através da interface.

---

## ⚙️ Funcionalidades

* Download de vídeos (MP4) com resolução de 360p até 1080p
* Download de áudios (MP3) com qualidade de 128kbps até 320kbps
* Interface gráfica simples e intuitiva (Tkinter)
* Status em tempo real (baixando, concluído ou erro)
* Execução em segundo plano (sem travar a interface)
* Memória de preferências (`config.json` salva automaticamente as configurações)

---

## 🧠 Tecnologias Utilizadas

* Python 3
* Tkinter (interface gráfica)
* yt-dlp (motor de download)
* threading (execução em segundo plano)
* subprocess (execução de comandos externos)
* json (salvar configurações)

---

## 🚀 Instalação

### 1. Instalar o Python

Abra o PowerShell como administrador e execute:

```bash
winget install Python.Python.3.12
```

---

### 2. Instalar o yt-dlp

Após instalar o Python, execute:

```bash
python -m pip install -U yt-dlp
```

---

## ▶️ Executando o Programa

Entre na pasta do projeto e execute:

```bash
python main.py
```

---

## 📝 Como Utilizar

1. Cole o link do vídeo ou música.
2. Escolha o formato:

   * MP4 (Vídeo)
   * MP3 (Áudio)
3. Escolha a qualidade desejada.
4. Escolha a pasta onde o arquivo será salvo.
5. Clique em **Baixar**.
6. Aguarde a conclusão do download.

---

## 🖥️ Sistemas Suportados

* Windows 10 ✔
* Windows 11 ✔ (testado)
* Linux ✔
* macOS ✔

---

## ⚠️ Observação

O projeto foi testado no Windows 11 e funciona com apenas duas dependências instaladas:

* Python
* yt-dlp

---

## ⚠️ Aviso Legal

Este projeto foi desenvolvido apenas para fins educacionais.

O usuário é responsável por garantir que o uso do software esteja de acordo com os direitos autorais e os termos das plataformas utilizadas, e o autor não se responsabiliza por qualquer uso indevido, danos, perda de dados ou violação de termos de serviço resultantes do uso deste software.

---

## 👨‍💻 Autor

Desenvolvido por **Guilherme (Guiboom)**
