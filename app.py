"""
Interface Web para o Sistema de Transcrição e Tradução
=======================================================
Versão otimizada para Hugging Face Spaces

Funcionalidades:
- Upload de arquivos de áudio
- Gravação via microfone no navegador
- Seleção de qualidade de transcrição
- Escolha de idioma de origem e destino
- Visualização de resultados em tempo real

Autor: João Vítor Arruda Percinotto
TCC: USO DE TRANSCRIÇÃO DE ÁUDIO PARA TRADUÇÃO DINÂMICA DE IDIOMAS COM MODELOS DE IA LLM
"""

import gradio as gr
from typing import Tuple, Optional
import os

# Importa o sistema integrado
from main import SistemaTranscricaoTraducao


# Cache global do sistema (evita recarregar modelo a cada uso)
_sistema_cache = {}

# Mapeamento de níveis de qualidade para modelos Whisper
QUALIDADE_PARA_MODELO = {
    "Muito Rápida": "tiny",
    "Rápida": "base",
    "Balanceada": "small",
    "Alta Qualidade": "medium",
    "Máxima Qualidade": "large"
}

# Mapeamento de idiomas (nome completo -> código)
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

# Idiomas de destino (sem opção de auto-detecção)
IDIOMAS_DESTINO = {k: v for k, v in IDIOMAS.items() if k != "Detecção Automática"}


def obter_sistema(modelo_whisper: str) -> SistemaTranscricaoTraducao:
    """
    Obtém ou cria uma instância do sistema com o modelo especificado.
    Usa cache para evitar recarregar o modelo desnecessariamente.
    """
    if modelo_whisper not in _sistema_cache:
        print(f"🔄 Carregando sistema com modelo '{modelo_whisper}'...")
        _sistema_cache[modelo_whisper] = SistemaTranscricaoTraducao(modelo_whisper=modelo_whisper)
    return _sistema_cache[modelo_whisper]


def processar_arquivo_audio(
    arquivo_audio,
    qualidade: str,
    idioma_origem: str,
    idioma_destino: str,
    traduzir: bool
) -> Tuple[str, str, str]:
    """
    Processa arquivo de áudio enviado pelo usuário.
    
    Returns:
        Tuple contendo:
        - Texto transcrito
        - Texto traduzido (ou mensagem se não traduzir)
        - Informações adicionais
    """
    if arquivo_audio is None:
        return "❌ Nenhum arquivo foi enviado.", "", ""
    
    try:
        # Converte qualidade para modelo Whisper
        modelo_whisper = QUALIDADE_PARA_MODELO[qualidade]
        
        # Converte nome do idioma para código
        codigo_idioma_destino = IDIOMAS_DESTINO[idioma_destino]
        codigo_idioma_origem = IDIOMAS.get(idioma_origem)
        
        # Se não for auto-detecção, usa o idioma especificado
        idioma_origem_transcricao = None if codigo_idioma_origem == "auto" else codigo_idioma_origem
        
        # Obtém o sistema com o modelo escolhido
        sistema = obter_sistema(modelo_whisper)
        
        # Processa a transcrição
        if idioma_origem_transcricao:
            resultado_transcricao = sistema.transcritor.transcrever_arquivo(
                arquivo_audio,
                idioma=idioma_origem_transcricao
            )
            resultado = {
                'arquivo': resultado_transcricao['arquivo'],
                'transcricao': resultado_transcricao,
                'traducao': None
            }
        else:
            resultado = sistema.processar_audio(
                caminho_audio=arquivo_audio,
                idioma_destino=codigo_idioma_destino,
                traduzir=False  # Vamos traduzir separadamente
            )
        
        # Extrai informações
        texto_transcrito = resultado['transcricao']['texto']
        idioma_detectado = resultado['transcricao']['idioma']
        
        # Traduz se solicitado
        if traduzir:
            traducao_resultado = sistema.tradutor.traduzir(
                texto=texto_transcrito,
                idioma_destino=codigo_idioma_destino,
                idioma_origem=idioma_detectado
            )
            texto_traduzido = traducao_resultado['texto_traduzido']
            servico = traducao_resultado['servico']
            
            # Encontra o nome do idioma detectado
            nome_idioma = next((k for k, v in IDIOMAS.items() if v == idioma_detectado), idioma_detectado)
            info = f"🌐 Idioma detectado: {nome_idioma}\n📝 Serviço de tradução: {servico}"
        else:
            texto_traduzido = "✅ Tradução não solicitada."
            nome_idioma = next((k for k, v in IDIOMAS.items() if v == idioma_detectado), idioma_detectado)
            info = f"🌐 Idioma detectado: {nome_idioma}"
        
        return texto_transcrito, texto_traduzido, info
        
    except Exception as e:
        print(f"❌ Erro ao processar áudio: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"❌ Erro ao processar áudio: {str(e)}", "", ""


def processar_microfone(
    audio_gravado,
    qualidade: str,
    idioma_origem: str,
    idioma_destino: str,
    traduzir: bool
) -> Tuple[str, str, str]:
    """
    Processa áudio gravado pelo microfone.
    
    Returns:
        Tuple contendo:
        - Texto transcrito
        - Texto traduzido (ou mensagem se não traduzir)
        - Informações adicionais
    """
    if audio_gravado is None:
        return "❌ Nenhuma gravação detectada.", "", ""
    
    try:
        # Usa a mesma função de processamento de arquivo
        return processar_arquivo_audio(
            audio_gravado,
            qualidade,
            idioma_origem,
            idioma_destino,
            traduzir
        )
        
    except Exception as e:
        print(f"❌ Erro ao processar gravação: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"❌ Erro ao processar gravação: {str(e)}", "", ""


def criar_interface():
    """Cria e configura a interface Gradio"""
    
    # Tema customizado
    tema = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="cyan",
    )
    
    with gr.Blocks(theme=tema, title="Transcrição e Tradução de Áudio") as interface:
        
        # Cabeçalho centralizado
        gr.HTML("""
        <div style="text-align: center; width: 100%; margin: 20px auto;">
            <h1 style="margin: 0;">🎙️ Sistema de Transcrição e Tradução de Áudio</h1>
            <h3 style="margin: 10px 0; font-weight: normal;">Ferramenta para transcrição automática de áudio usando Whisper e tradução com Google Translate</h3>
        </div>
        """)
        
        gr.Markdown("---")
        
        # Informações sobre o projeto
        with gr.Accordion("ℹ️ Sobre o Projeto", open=False):
            gr.Markdown("""
            ### TCC: Uso de Transcrição de Áudio para Tradução Dinâmica de Idiomas com Modelos de IA LLM
            
            **Autor:** João Vítor Arruda Percinotto
            
            **Descrição:** Sistema desenvolvido para transcrever automaticamente áudios em diversos idiomas 
            usando o modelo Whisper da OpenAI e realizar traduções em tempo real utilizando Google Translate.
            
            **Recursos:**
            - ✅ Transcrição de áudio em 12+ idiomas
            - ✅ Tradução automática entre idiomas
            - ✅ Upload de arquivos de áudio
            - ✅ Gravação via microfone (recomendado Chrome/Edge)
            - ✅ Múltiplos níveis de qualidade de transcrição
            
            **Formatos de áudio suportados:** MP3, WAV, OPUS, M4A, FLAC, OGG, WMA
            """)
        
        # Aviso sobre compatibilidade de navegadores
        gr.Markdown("""
        ℹ️ **Nota:** Para melhor experiência com a gravação via microfone, 
        use **Google Chrome** ou **Microsoft Edge**.
        """)
        
        # Abas para diferentes modos
        with gr.Tabs():
            
            # === ABA 1: UPLOAD DE ARQUIVO ===
            with gr.Tab("📁 Upload de Arquivo"):
                gr.Markdown("### Envie um arquivo de áudio para transcrever e traduzir")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        # Inputs
                        arquivo_input = gr.Audio(
                            label="Arquivo de Áudio (MP3, WAV, OPUS, M4A, FLAC, OGG, WMA)",
                            type="filepath",
                            sources=["upload"]
                        )
                        
                        qualidade_arquivo = gr.Radio(
                            choices=["Muito Rápida", "Rápida", "Balanceada", "Alta Qualidade", "Máxima Qualidade"],
                            value="Balanceada",
                            label="Nível de Qualidade da Transcrição",
                            info="Quanto maior a qualidade, mais lenta e precisa será a transcrição"
                        )
                        
                        idioma_origem_arquivo = gr.Dropdown(
                            choices=list(IDIOMAS.keys()),
                            value="Detecção Automática",
                            label="Idioma do Áudio (Opcional)",
                            info="Deixe em 'Detecção Automática' se não souber o idioma"
                        )
                        
                        idioma_destino_arquivo = gr.Dropdown(
                            choices=list(IDIOMAS_DESTINO.keys()),
                            value="Inglês",
                            label="Idioma de Destino para Tradução",
                            info="Idioma para o qual o texto será traduzido"
                        )
                        
                        traduzir_arquivo = gr.Checkbox(
                            value=True,
                            label="Traduzir texto transcrito",
                            info="Desmarque para apenas transcrever (sem tradução)"
                        )
                        
                        btn_processar_arquivo = gr.Button(
                            "🚀 Processar Arquivo",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        # Outputs
                        transcricao_arquivo = gr.Textbox(
                            label="📝 Texto Transcrito",
                            lines=8,
                            max_lines=15,
                            show_copy_button=True
                        )
                        
                        traducao_arquivo = gr.Textbox(
                            label="🌍 Texto Traduzido",
                            lines=8,
                            max_lines=15,
                            show_copy_button=True
                        )
                        
                        info_arquivo = gr.Textbox(
                            label="ℹ️ Informações",
                            lines=2
                        )
                
                # Conecta o botão à função
                btn_processar_arquivo.click(
                    fn=processar_arquivo_audio,
                    inputs=[arquivo_input, qualidade_arquivo, idioma_origem_arquivo, idioma_destino_arquivo, traduzir_arquivo],
                    outputs=[transcricao_arquivo, traducao_arquivo, info_arquivo]
                )
            
            # === ABA 2: GRAVAÇÃO VIA MICROFONE ===
            with gr.Tab("🎤 Gravar Microfone"):
                gr.Markdown("### Grave sua voz diretamente pelo navegador")
                gr.Markdown("""
                **📝 Como usar:**
                1. Clique no ícone do microfone para começar a gravar
                2. Fale claramente
                3. Clique novamente para parar a gravação
                4. Clique no botão "🚀 Processar Gravação"
                
                **⚠️ Problemas com o microfone?**
                - Verifique se o navegador tem permissão para acessar o microfone
                - Use preferencialmente Chrome ou Edge
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        # Inputs
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
                            value="Português",
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
                        # Outputs
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
                
                # Conecta o botão à função
                btn_processar_mic.click(
                    fn=processar_microfone,
                    inputs=[microfone_input, qualidade_mic, idioma_origem_mic, idioma_destino_mic, traduzir_mic],
                    outputs=[transcricao_mic, traducao_mic, info_mic]
                )
        
        # Rodapé
        gr.Markdown("---")
        gr.Markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9em;">
        
        **TCC:** Uso de Transcrição de Áudio para Tradução Dinâmica de Idiomas com Modelos de IA LLM  
        **Autor:** João Vítor Arruda Percinotto
        
        </div>
        """)
    
    return interface


# Cria e inicia a interface
"""
Interface Web para o Sistema de Transcrição e Tradução
=======================================================
Interface gráfica web usando Gradio para o sistema de transcrição
e tradução automática de áudio.

Autor: João Vítor Arruda Percinotto
TCC: USO DE TRANSCRIÇÃO DE ÁUDIO PARA TRADUÇÃO DINÂMICA DE IDIOMAS COM MODELOS DE IA LLM
"""

import gradio as gr
from typing import Tuple
import whisper
from deep_translator import GoogleTranslator, MyMemoryTranslator
from langdetect import detect
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning)

# Cache de modelos
_modelos_cache = {}

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
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
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
        
        # Informações sobre compatibilidade
        gr.Markdown("""
        ℹ️ **Nota:** Para melhor experiência com a gravação via microfone, 
        recomenda-se o uso do **Google Chrome** ou **Microsoft Edge**.
        """)
        
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
                            value="Português",
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
                gr.Markdown("""
                **📝 Como usar:**
                1. Clique no ícone do microfone para começar a gravar
                2. Fale claramente
                3. Clique novamente para parar a gravação
                4. Clique no botão "🚀 Processar Gravação"
                """)
                
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
                            value="Português",
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
    
    # Detecta se está no Hugging Face Spaces
    is_spaces = os.getenv("SPACE_ID") is not None
    
    interface = criar_interface()
    
    if is_spaces:
        # No Hugging Face Spaces
        interface.launch(server_name="0.0.0.0", server_port=7860)
    else:
        # Execução local
        interface.launch(inbrowser=True)