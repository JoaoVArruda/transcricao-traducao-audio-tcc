"""
Interface Web para o Sistema de Transcrição e Tradução
=======================================================
Arquivo principal para deploy no Hugging Face Spaces

Autor: João Vítor Arruda Percinotto
TCC: USO DE TRANSCRIÇÃO DE ÁUDIO PARA TRADUÇÃO DINÂMICA DE IDIOMAS COM MODELOS DE IA LLM
"""

import gradio as gr
from typing import Tuple
import whisper
from deep_translator import GoogleTranslator, MyMemoryTranslator
from langdetect import detect
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


# Mapeamento de níveis de qualidade para modelos Whisper
QUALIDADE_PARA_MODELO = {
    "Muito Rápida": "tiny",
    "Rápida": "base",
    "Balanceada": "small",
    "Alta Qualidade": "medium",
    "Máxima Qualidade": "large"
}

# Mapeamento de idiomas
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

IDIOMAS_DESTINO = {k: v for k, v in IDIOMAS.items() if k != "Detecção Automática"}

# Cache de modelos
_modelos_cache = {}


def carregar_modelo_whisper(modelo: str):
    """Carrega e cacheia o modelo Whisper"""
    if modelo not in _modelos_cache:
        print(f"🔄 Carregando modelo Whisper '{modelo}'...")
        _modelos_cache[modelo] = whisper.load_model(modelo)
        print(f"✅ Modelo '{modelo}' carregado!")
    return _modelos_cache[modelo]


def transcrever_audio(arquivo_audio, modelo_nome: str, idioma: str = None):
    """Transcreve áudio usando Whisper"""
    modelo = carregar_modelo_whisper(modelo_nome)
    
    opcoes = {
        "fp16": False,
        "verbose": False
    }
    
    if idioma and idioma != "auto":
        opcoes["language"] = idioma
    
    resultado = modelo.transcribe(arquivo_audio, **opcoes)
    return resultado["text"].strip(), resultado.get("language", "desconhecido")


def traduzir_texto(texto: str, idioma_destino: str, idioma_origem: str = None):
    """Traduz texto usando Google Translate"""
    if not texto or not texto.strip():
        return texto, "nenhum"
    
    # Detecta idioma se não especificado
    if not idioma_origem:
        idioma_origem = detect(texto)
    
    # Verifica se já está no idioma desejado
    if idioma_origem == idioma_destino:
        return texto, "nenhum (mesma lingua)"
    
    try:
        tradutor = GoogleTranslator(source=idioma_origem, target=idioma_destino)
        return tradutor.translate(texto), "Google Translate"
    except Exception as e_google:
        try:
            tradutor = MyMemoryTranslator(source=idioma_origem, target=idioma_destino)
            return tradutor.translate(texto), "MyMemory"
        except Exception as e_mymemory:
            return f"❌ Erro ao traduzir: {str(e_google)}", "erro"


def processar_audio(
    arquivo_audio,
    qualidade: str,
    idioma_origem: str,
    idioma_destino: str,
    traduzir: bool
) -> Tuple[str, str, str]:
    """Processa áudio completo: transcrição e tradução"""
    
    if arquivo_audio is None:
        return "❌ Nenhum arquivo foi enviado.", "", ""
    
    try:
        # Converte qualidade para modelo Whisper
        modelo_whisper = QUALIDADE_PARA_MODELO[qualidade]
        
        # Converte nomes de idioma para códigos
        codigo_idioma_destino = IDIOMAS_DESTINO[idioma_destino]
        codigo_idioma_origem = IDIOMAS.get(idioma_origem)
        
        # Transcreve
        print(f"🎙️ Transcrevendo com modelo {modelo_whisper}...")
        idioma_transcricao = None if codigo_idioma_origem == "auto" else codigo_idioma_origem
        texto_transcrito, idioma_detectado = transcrever_audio(
            arquivo_audio,
            modelo_whisper,
            idioma_transcricao
        )
        
        print(f"✅ Transcrição concluída! Idioma: {idioma_detectado}")
        
        # Traduz se solicitado
        if traduzir:
            print(f"🌍 Traduzindo para {idioma_destino}...")
            texto_traduzido, servico = traduzir_texto(
                texto_transcrito,
                codigo_idioma_destino,
                idioma_detectado
            )
            
            nome_idioma = next((k for k, v in IDIOMAS.items() if v == idioma_detectado), idioma_detectado)
            info = f"🌐 Idioma detectado: {nome_idioma}\n📝 Serviço de tradução: {servico}"
        else:
            texto_traduzido = "✅ Tradução não solicitada."
            nome_idioma = next((k for k, v in IDIOMAS.items() if v == idioma_detectado), idioma_detectado)
            info = f"🌐 Idioma detectado: {nome_idioma}"
        
        return texto_transcrito, texto_traduzido, info
        
    except Exception as e:
        return f"❌ Erro ao processar áudio: {str(e)}", "", ""


def criar_interface():
    """Cria a interface Gradio"""
    
    tema = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="cyan",
    )
    
    with gr.Blocks(theme=tema, title="Transcrição e Tradução de Áudio") as interface:
        
        gr.HTML("""
        <div style="text-align: center; width: 100%; margin: 20px auto;">
            <h1 style="margin: 0;">🎙️ Sistema de Transcrição e Tradução de Áudio</h1>
            <h3 style="margin: 10px 0; font-weight: normal;">Ferramenta para transcrição automática de áudio usando Whisper e tradução com Google Translate</h3>
        </div>
        """)
        
        gr.Markdown("---")
        
        with gr.Tabs():
            # ABA: Upload de Arquivo
            with gr.Tab("📁 Upload de Arquivo"):
                gr.Markdown("### Envie um arquivo de áudio para transcrever e traduzir")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        arquivo_input = gr.Audio(
                            label="Arquivo de Áudio (MP3, WAV, OPUS, M4A, FLAC, OGG, WMA)",
                            type="filepath",
                            sources=["upload"]
                        )
                        
                        qualidade = gr.Radio(
                            choices=["Muito Rápida", "Rápida", "Balanceada", "Alta Qualidade", "Máxima Qualidade"],
                            value="Balanceada",
                            label="Nível de Qualidade da Transcrição",
                            info="Quanto maior a qualidade, mais lenta e precisa será a transcrição"
                        )
                        
                        idioma_origem = gr.Dropdown(
                            choices=list(IDIOMAS.keys()),
                            value="Detecção Automática",
                            label="Idioma do Áudio (Opcional)",
                            info="Deixe em 'Detecção Automática' se não souber o idioma"
                        )
                        
                        idioma_destino = gr.Dropdown(
                            choices=list(IDIOMAS_DESTINO.keys()),
                            value="Inglês",
                            label="Idioma de Destino para Tradução",
                            info="Idioma para o qual o texto será traduzido"
                        )
                        
                        traduzir = gr.Checkbox(
                            value=True,
                            label="Traduzir texto transcrito",
                            info="Desmarque para apenas transcrever (sem tradução)"
                        )
                        
                        btn_processar = gr.Button(
                            "🚀 Processar Arquivo",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        transcricao = gr.Textbox(
                            label="📝 Texto Transcrito",
                            lines=8,
                            max_lines=15,
                            show_copy_button=True
                        )
                        
                        traducao = gr.Textbox(
                            label="🌍 Texto Traduzido",
                            lines=8,
                            max_lines=15,
                            show_copy_button=True
                        )
                        
                        info = gr.Textbox(
                            label="ℹ️ Informações",
                            lines=2
                        )
                
                btn_processar.click(
                    fn=processar_audio,
                    inputs=[arquivo_input, qualidade, idioma_origem, idioma_destino, traduzir],
                    outputs=[transcricao, traducao, info]
                )
            
            # ABA: Microfone
            with gr.Tab("🎤 Gravar Microfone"):
                gr.Markdown("### Grave sua voz diretamente pelo navegador")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        microfone_input = gr.Audio(
                            label="Gravação de Áudio",
                            type="filepath",
                            sources=["microphone"]
                        )
                        
                        qualidade_mic = gr.Radio(
                            choices=["Muito Rápida", "Rápida", "Balanceada", "Alta Qualidade", "Máxima Qualidade"],
                            value="Balanceada",
                            label="Nível de Qualidade da Transcrição",
                            info="Quanto maior a qualidade, mais lenta e precisa será a transcrição"
                        )
                        
                        idioma_origem_mic = gr.Dropdown(
                            choices=list(IDIOMAS.keys()),
                            value="Detecção Automática",
                            label="Idioma do Áudio (Opcional)",
                            info="Deixe em 'Detecção Automática' se não souber o idioma"
                        )
                        
                        idioma_destino_mic = gr.Dropdown(
                            choices=list(IDIOMAS_DESTINO.keys()),
                            value="Inglês",
                            label="Idioma de Destino para Tradução",
                            info="Idioma para o qual o texto será traduzido"
                        )
                        
                        traduzir_mic = gr.Checkbox(
                            value=True,
                            label="Traduzir texto transcrito",
                            info="Desmarque para apenas transcrever (sem tradução)"
                        )
                        
                        btn_processar_mic = gr.Button(
                            "🚀 Processar Gravação",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        transcricao_mic = gr.Textbox(
                            label="📝 Texto Transcrito",
                            lines=8,
                            max_lines=15,
                            show_copy_button=True
                        )
                        
                        traducao_mic = gr.Textbox(
                            label="🌍 Texto Traduzido",
                            lines=8,
                            max_lines=15,
                            show_copy_button=True
                        )
                        
                        info_mic = gr.Textbox(
                            label="ℹ️ Informações",
                            lines=2
                        )
                
                btn_processar_mic.click(
                    fn=processar_audio,
                    inputs=[microfone_input, qualidade_mic, idioma_origem_mic, idioma_destino_mic, traduzir_mic],
                    outputs=[transcricao_mic, traducao_mic, info_mic]
                )
        
        gr.Markdown("---")
        gr.Markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9em;">
        
        **TCC:** Uso de Transcrição de Áudio para Tradução Dinâmica de Idiomas com Modelos de IA LLM  
        **Autor:** João Vítor Arruda Percinotto
        
        </div>
        """)
    
    return interface


if __name__ == "__main__":
    print("🚀 Iniciando Sistema de Transcrição e Tradução...")
    interface = criar_interface()
    interface.launch()