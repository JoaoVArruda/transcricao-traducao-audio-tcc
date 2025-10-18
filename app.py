"""
Sistema de Transcrição e Tradução de Áudio
Autor: João Vítor Arruda Percinotto
TCC: USO DE TRANSCRIÇÃO DE ÁUDIO PARA TRADUÇÃO DINÂMICA DE IDIOMAS COM MODELOS DE IA LLM
"""

import gradio as gr
import whisper
from deep_translator import GoogleTranslator
from langdetect import detect
import warnings

warnings.filterwarnings("ignore")

# Mapeamentos
QUALIDADE = {
    "Muito Rápida": "tiny",
    "Rápida": "base", 
    "Balanceada": "small",
    "Alta Qualidade": "medium",
    "Máxima Qualidade": "large"
}

IDIOMAS = {
    "Detecção Automática": "auto",
    "Português": "pt",
    "Inglês": "en",
    "Espanhol": "es",
    "Francês": "fr",
    "Alemão": "de",
    "Italiano": "it",
    "Japonês": "ja",
    "Coreano": "ko",
    "Chinês (Simplificado)": "zh-CN",
    "Russo": "ru",
    "Árabe": "ar"
}

IDIOMAS_DEST = {k: v for k, v in IDIOMAS.items() if k != "Detecção Automática"}

# Cache
_cache = {}

def carregar_modelo(nome):
    if nome not in _cache:
        _cache[nome] = whisper.load_model(nome)
    return _cache[nome]

def processar(audio, qual, orig, dest, trad):
    if audio is None:
        return "❌ Nenhum arquivo enviado.", "", ""
    
    try:
        modelo = carregar_modelo(QUALIDADE[qual])
        cod_dest = IDIOMAS_DEST[dest]
        cod_orig = IDIOMAS.get(orig)
        
        # Transcreve
        opts = {"fp16": False, "verbose": False}
        if cod_orig and cod_orig != "auto":
            opts["language"] = cod_orig
        
        resultado = modelo.transcribe(audio, **opts)
        texto = resultado["text"].strip()
        idioma = resultado.get("language", "desconhecido")
        
        # Nome do idioma
        nome_idioma = next((k for k, v in IDIOMAS.items() if v == idioma), idioma)
        
        # Traduz
        if trad:
            if idioma == cod_dest:
                return texto, texto, f"🌐 Idioma: {nome_idioma}\n⚠️ Já está no idioma desejado"
            
            tradutor = GoogleTranslator(source=idioma, target=cod_dest)
            traduzido = tradutor.translate(texto)
            return texto, traduzido, f"🌐 Idioma detectado: {nome_idioma}\n📝 Google Translate"
        else:
            return texto, "✅ Tradução não solicitada", f"🌐 Idioma detectado: {nome_idioma}"
    
    except Exception as e:
        return f"❌ Erro: {str(e)}", "", ""

# Interface
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as app:
    gr.HTML("""
        <div style="text-align: center; margin: 20px;">
            <h1>🎙️ Sistema de Transcrição e Tradução de Áudio</h1>
            <h3 style="font-weight: normal;">Transcrição automática com Whisper e tradução com Google Translate</h3>
        </div>
    """)
    
    gr.Markdown("---")
    
    with gr.Tabs():
        with gr.Tab("📁 Upload de Arquivo"):
            gr.Markdown("### Envie um arquivo de áudio")
            
            with gr.Row():
                with gr.Column():
                    arq = gr.Audio(label="Arquivo (MP3, WAV, OPUS, M4A, FLAC, OGG, WMA)", type="filepath", sources=["upload"])
                    qual1 = gr.Radio(["Muito Rápida", "Rápida", "Balanceada", "Alta Qualidade", "Máxima Qualidade"], 
                                    value="Balanceada", label="Qualidade da Transcrição")
                    orig1 = gr.Dropdown(list(IDIOMAS.keys()), value="Detecção Automática", 
                                       label="Idioma do Áudio (Opcional)")
                    dest1 = gr.Dropdown(list(IDIOMAS_DEST.keys()), value="Inglês", 
                                       label="Idioma de Destino")
                    trad1 = gr.Checkbox(value=True, label="Traduzir texto transcrito")
                    btn1 = gr.Button("🚀 Processar", variant="primary", size="lg")
                
                with gr.Column():
                    trans1 = gr.Textbox(label="📝 Texto Transcrito", lines=8, show_copy_button=True)
                    trad1_out = gr.Textbox(label="🌍 Texto Traduzido", lines=8, show_copy_button=True)
                    info1 = gr.Textbox(label="ℹ️ Informações", lines=2)
            
            btn1.click(processar, [arq, qual1, orig1, dest1, trad1], [trans1, trad1_out, info1])
        
        with gr.Tab("🎤 Gravar Microfone"):
            gr.Markdown("### Grave sua voz diretamente")
            
            with gr.Row():
                with gr.Column():
                    mic = gr.Audio(label="Gravação", type="filepath", sources=["microphone"])
                    qual2 = gr.Radio(["Muito Rápida", "Rápida", "Balanceada", "Alta Qualidade", "Máxima Qualidade"], 
                                    value="Balanceada", label="Qualidade da Transcrição")
                    orig2 = gr.Dropdown(list(IDIOMAS.keys()), value="Detecção Automática", 
                                       label="Idioma do Áudio (Opcional)")
                    dest2 = gr.Dropdown(list(IDIOMAS_DEST.keys()), value="Inglês", 
                                       label="Idioma de Destino")
                    trad2 = gr.Checkbox(value=True, label="Traduzir texto transcrito")
                    btn2 = gr.Button("🚀 Processar", variant="primary", size="lg")
                
                with gr.Column():
                    trans2 = gr.Textbox(label="📝 Texto Transcrito", lines=8, show_copy_button=True)
                    trad2_out = gr.Textbox(label="🌍 Texto Traduzido", lines=8, show_copy_button=True)
                    info2 = gr.Textbox(label="ℹ️ Informações", lines=2)
            
            btn2.click(processar, [mic, qual2, orig2, dest2, trad2], [trans2, trad2_out, info2])
    
    gr.Markdown("---")
    gr.HTML("""
        <div style="text-align: center; color: #666; font-size: 0.9em;">
        <strong>TCC:</strong> Uso de Transcrição de Áudio para Tradução Dinâmica de Idiomas com Modelos de IA LLM<br>
        <strong>Autor:</strong> João Vítor Arruda Percinotto
        </div>
    """)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)