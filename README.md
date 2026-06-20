markdown
# PyMediaDownloader

Aplicativo prático para download de vídeos e áudios, com interface gráfica desenvolvida inteiramente em Python.

---

## 📌 Sobre o Projeto

O PyMediaDownloader foi criado como um projeto de aprendizado para explorar o desenvolvimento de interfaces gráficas em Python. Foi minha primeira experiência criando uma aplicação com interface visual, saindo dos programas executados apenas pelo terminal.

O projeto utiliza o poderoso `yt-dlp` no backend para realizar os downloads, oferecendo uma experiência simples e amigável para o usuário final através da interface.

---

## ⚙️ Funcionalidades

- Download de vídeos (MP4) com resolução de 360p até 1080p
- Download de áudios (MP3) com qualidade de 128kbps até 320kbps
- Interface gráfica simples e intuitiva (Tkinter)
- Status em tempo real (baixando, concluído ou erro)
- Execução em segundo plano (sem travar a interface)
- Memória de preferências (`config.json` salva automaticamente configurações)

---

## 🧠 Tecnologias Utilizadas

- **Python 3**
- **Tkinter** (interface gráfica)
- **yt-dlp** (motor de download)
- **threading** (execução em segundo plano)
- **subprocess** (execução de comandos externos)
- **json** (salvar configurações)

---

## 🎯 Objetivos de Aprendizado

Durante o desenvolvimento deste projeto, pratiquei:

- Criação de interfaces gráficas (GUI) com Python
- Execução de processos em background com `threading`
- Integração de ferramentas externas (`yt-dlp`)
- Uso de `subprocess` para comandos do sistema
- Manipulação de arquivos JSON
- Tratamento básico de erros e estados da interface

---

## 🚀 Como Usar (SIMPLES)

### 1. Abrir o programa
Execute:

python main.py



### 2. Colocar o link

Cole o link do vídeo ou música no campo **"Link"**.

### 3. Escolher o formato

* **MP4 (Vídeo)** → baixa vídeo com áudio
* **MP3 (Áudio)** → extrai apenas o áudio

### 4. Escolher a qualidade

* **Vídeo:** 360p até 1080p
* **Áudio:** 128kbps até 320kbps

### 5. Escolher a pasta

Clique em **“Alterar Pasta”** para definir onde os arquivos serão salvos.

### 6. Baixar

Clique em **“Baixar”** e aguarde o status na tela.

---

## ⚠️ IMPORTANTE — FFmpeg (OBRIGATÓRIO)

O **FFmpeg** é necessário para o funcionamento correto do programa. Ele é responsável por:

* Juntar áudio e vídeo em um único arquivo
* Converter vídeos corretamente para MP4
* Converter áudio para MP3
* Evitar arquivos em formato WEBM incompleto

> **Nota:** Sem ele, alguns downloads podem falhar ou sair sem áudio.

### 📥 Instalação do FFmpeg (Windows)

1. **Baixar:** Acesse [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. **Baixar a versão:** Escolha a opção `ffmpeg-release-full`
3. **Extrair:** Extraia o arquivo `.7z` usando o 7-Zip.
4. **Localizar o executável:** Entre na pasta `bin`.
5. **Copiar arquivo:** Copie o arquivo `ffmpeg.exe`.
6. **Colocar no projeto:** Coloque dentro da pasta do projeto, conforme a estrutura abaixo:
text
PyDownloader/
 ├── main.py
 └── ffmpeg.exe





### 🐧 Linux


sudo apt install ffmpeg



### 🍎 Mac


brew install ffmpeg



---

## 📂 Estrutura do projeto (final)

text
PyDownloader/
 ├── main.py
 ├── config.json
 └── ffmpeg.exe



---

## ⚠️ Aviso Legal

Este projeto foi desenvolvido apenas para fins educacionais. O usuário é responsável por garantir que o uso do software esteja de acordo com os direitos autorais e os termos das plataformas utilizadas, e o autor não se responsabiliza por qualquer uso indevido, danos, perda de dados ou violação de termos de serviço resultantes do uso deste software.

---

## 👨‍💻 Autor

Desenvolvido por **Guilherme (Guiboom)**



