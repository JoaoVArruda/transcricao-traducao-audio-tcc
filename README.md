---
title: Sistema de Transcrição e Tradução de Áudio
emoji: 🎙️
colorFrom: blue
colorTo: cyan
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# 🎙️ Sistema de Transcrição e Tradução de Áudio

Ferramenta para transcrição automática de áudio usando **Whisper** (OpenAI) e tradução com **Google Translate**.

## 📋 Sobre o Projeto

Este sistema foi desenvolvido como parte do **Trabalho de Conclusão de Curso (TCC)** com o tema:

> **USO DE TRANSCRIÇÃO DE ÁUDIO PARA TRADUÇÃO DINÂMICA DE IDIOMAS COM MODELOS DE IA LLM**

**Autor:** João Vítor Arruda Percinotto

## ✨ Funcionalidades

- 🎤 **Upload de arquivos de áudio** (MP3, WAV, OPUS, M4A, FLAC, OGG, WMA)
- 🎙️ **Gravação via microfone** direto no navegador
- 🔍 **Detecção automática de idioma** ou seleção manual
- 🌍 **Tradução automática** para 11 idiomas
- ⚙️ **5 níveis de qualidade** de transcrição
- 📝 **Interface intuitiva** e responsiva

## 🚀 Como Usar

1. **Escolha o modo:**
   - 📁 Upload de arquivo de áudio
   - 🎤 Gravar pelo microfone

2. **Configure:**
   - Selecione o nível de qualidade da transcrição
   - (Opcional) Escolha o idioma do áudio
   - Selecione o idioma de destino para tradução
   - Marque/desmarque a opção de traduzir

3. **Processe:**
   - Clique em "🚀 Processar" e aguarde
   - Veja o texto transcrito e traduzido

## 🌐 Idiomas Suportados

- 🇧🇷 Português
- 🇺🇸 Inglês
- 🇪🇸 Espanhol
- 🇫🇷 Francês
- 🇩🇪 Alemão
- 🇮🇹 Italiano
- 🇯🇵 Japonês
- 🇰🇷 Coreano
- 🇨🇳 Chinês (Simplificado)
- 🇷🇺 Russo
- 🇸🇦 Árabe

## ⚙️ Níveis de Qualidade

| Nível | Modelo Whisper | Velocidade | Precisão | Tamanho |
|-------|----------------|------------|----------|---------|
| Muito Rápida | tiny | ⚡⚡⚡ | ⭐⭐ | ~39 MB |
| Rápida | base | ⚡⚡ | ⭐⭐⭐ | ~74 MB |
| Balanceada | small | ⚡ | ⭐⭐⭐⭐ | ~244 MB |
| Alta Qualidade | medium | 🐢 | ⭐⭐⭐⭐⭐ | ~769 MB |
| Máxima Qualidade | large | 🐌 | ⭐⭐⭐⭐⭐ | ~1.5 GB |

## 🛠️ Tecnologias Utilizadas

- **Whisper (OpenAI)** - Transcrição de áudio com IA
- **Deep Translator** - Tradução multilíngue
- **Gradio** - Interface web interativa
- **Python 3.10+** - Linguagem de programação

## 📦 Dependências

```
openai-whisper
deep-translator
langdetect
gradio
ffmpeg-python
```

## 💻 Executar Localmente

```bash
# Clone o repositório
git clone <seu-repositorio>

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python app.py
```

## 📝 Licença

Este projeto está sob a licença MIT.

## 👨‍🎓 Autor

**João Vítor Arruda Percinotto**

Trabalho de Conclusão de Curso (TCC)  
Tema: Uso de Transcrição de Áudio para Tradução Dinâmica de Idiomas com Modelos de IA LLM

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!