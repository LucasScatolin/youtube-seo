import streamlit as st
from openai import OpenAI
import os
import re
from pydub import AudioSegment
import tempfile
from dotenv import load_dotenv
import time
import yt_dlp

# Load environment variables
load_dotenv()

# Get API key from Streamlit secrets or environment variables
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv('OPENAI_API_KEY')
if not api_key:
    st.error('⚠️ OpenAI API key not found. Please set it in your .env file or Streamlit secrets.')
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def sanitize_filename(filename):
    # Remove any characters that aren't alphanumeric, space, or hyphen
    sanitized = re.sub(r'[^\w\s-]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def download_youtube_audio(youtube_url):
    try:
        st.write("Iniciando download do vídeo...")
        
        temp_dir = tempfile.gettempdir()
        temp_filename = 'youtube_audio_' + str(int(time.time()))
        output_template = os.path.join(temp_dir, temp_filename)

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'quiet': True,
            'no_warnings': True
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_title = info.get('title', '')
            st.write(f"Título do vídeo: {video_title}")
            st.write(f"Duração: {info.get('duration', 0)} segundos")
            
            st.write("Baixando áudio...")
            ydl.download([youtube_url])
        
        output_path = output_template + '.wav'
        st.write("Download concluído!")
        
        return output_path, video_title
        
    except Exception as e:
        st.error(f"Erro ao baixar vídeo: {str(e)}")
        raise e

def split_audio(file_path, max_size_bytes=25000000):
    try:
        st.write("Dividindo áudio em partes menores...")
        
        if not os.path.exists(file_path):
            raise Exception(f"Arquivo de áudio não encontrado: {file_path}")
            
        audio = AudioSegment.from_wav(file_path)
        total_size_bytes = len(audio.raw_data)
        chunk_length_ms = int((max_size_bytes / total_size_bytes) * len(audio))
        
        chunks = []
        for i in range(0, len(audio), chunk_length_ms):
            chunks.append(audio[i:i + chunk_length_ms])
        
        st.write(f"Áudio dividido em {len(chunks)} partes")
        return chunks
    except Exception as e:
        st.error(f"Erro ao dividir áudio: {str(e)}")
        raise e

def transcribe_audio(audio_segment):
    try:
        temp_file = os.path.join(tempfile.gettempdir(), f"temp_segment_{int(time.time())}.wav")
        audio_segment.export(temp_file, format="wav")
        
        with open(temp_file, "rb") as audio_file:
            transcription_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        os.remove(temp_file)
        return transcription_response.text
    except Exception as e:
        st.error(f"Erro na transcrição: {str(e)}")
        raise e

def generate_article_outline(transcript):
    try:
        st.write("Gerando estrutura do artigo...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em SEO que cria estruturas de artigos em português brasileiro. "
                              "Crie uma estrutura de artigo independente e original, focando apenas no tema e nas informações, "
                              "sem mencionar a fonte do conteúdo ou referências ao material original."
                },
                {
                    "role": "user",
                    "content": f"Usando estas informações como base de conhecimento, crie uma estrutura de artigo SEO em português brasileiro sobre o tema:\n\n{transcript}"
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao gerar estrutura do artigo: {str(e)}")
        raise e

def write_full_article(transcript, outline):
    try:
        st.write("Escrevendo artigo completo...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um redator especializado em criar artigos em português brasileiro. "
                              "Crie um artigo original e independente, focando apenas no tema e nas informações apresentadas. "
                              "Não mencione a fonte do conteúdo, vídeos, autores originais ou qualquer referência ao material fonte. "
                              "O artigo deve ser uma peça independente que aborda o tema de forma profissional e objetiva. "
                              "O artigo DEVE ter no mínimo 600 palavras, sendo rico em detalhes e informações relevantes para SEO."
                },
                {
                    "role": "user",
                    "content": f"Estrutura do artigo:\n{outline}\n\nBase de conhecimento:\n{transcript}\n\n"
                              "Crie um artigo completo e original em português brasileiro seguindo esta estrutura. "
                              "O artigo deve ter no mínimo 600 palavras. Desenvolva cada seção com profundidade, "
                              "incluindo exemplos práticos, dados técnicos e informações detalhadas quando relevante."
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        article = response.choices[0].message.content
        
        word_count = len(article.split())
        
        if word_count < 600:
            st.write("Expandindo artigo para atingir o mínimo de 600 palavras...")
            expansion_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um redator especializado em expandir artigos mantendo a qualidade e relevância do conteúdo. "
                                 "Expanda o artigo fornecido para atingir no mínimo 600 palavras, adicionando mais detalhes, "
                                 "exemplos e informações relevantes."
                    },
                    {
                        "role": "user",
                        "content": f"Artigo atual ({word_count} palavras):\n{article}\n\n"
                                 "Base de conhecimento adicional:\n{transcript}\n\n"
                                 "Expanda este artigo para ter no mínimo 600 palavras, mantendo a qualidade e coerência. "
                                 "Adicione mais detalhes, exemplos práticos e informações técnicas relevantes."
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            article = expansion_response.choices[0].message.content
        
        return article
    except Exception as e:
        st.error(f"Erro ao escrever artigo: {str(e)}")
        raise e

def review_article(transcript, article):
    try:
        st.write("Revisando artigo...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um revisor especializado em verificar a precisão técnica e factual de artigos em português brasileiro. "
                              "Compare o artigo com a transcrição original e identifique quaisquer discrepâncias, erros ou pontos que precisam "
                              "ser melhorados. Forneça uma análise detalhada das correções necessárias."
                },
                {
                    "role": "user",
                    "content": f"Base de conhecimento (transcrição):\n{transcript}\n\nArtigo para revisar:\n{article}\n\n"
                              "Compare o artigo com a transcrição e forneça uma análise detalhada das correções necessárias. "
                              "Identifique:\n"
                              "1. Informações incorretas ou imprecisas\n"
                              "2. Conceitos mal interpretados\n"
                              "3. Pontos importantes da transcrição que foram omitidos\n"
                              "4. Sugestões de melhorias na estrutura e clareza"
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro na revisão do artigo: {str(e)}")
        raise e

def create_final_version(transcript, initial_article, review_feedback):
    try:
        st.write("Criando versão final do artigo...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um redator especializado em criar a versão final de artigos em português brasileiro. "
                              "Use o artigo inicial e o feedback da revisão para criar uma versão final aprimorada, "
                              "mantendo o mínimo de 600 palavras e incorporando todas as correções necessárias."
                },
                {
                    "role": "user",
                    "content": f"Artigo inicial:\n{initial_article}\n\n"
                              f"Feedback da revisão:\n{review_feedback}\n\n"
                              f"Base de conhecimento (transcrição):\n{transcript}\n\n"
                              "Crie a versão final do artigo, incorporando as correções e melhorias sugeridas na revisão. "
                              "Mantenha o artigo com no mínimo 600 palavras e garanta que todas as informações estejam "
                              "precisas e alinhadas com a transcrição original."
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao criar versão final do artigo: {str(e)}")
        raise e

def main():
    st.title("Gerador de Artigos SEO a partir de Vídeos do YouTube")
    
    youtube_url = st.text_input(
        "Cole o URL do vídeo do YouTube:",
        help="Exemplo: https://www.youtube.com/watch?v=XXXX ou https://youtu.be/XXXX"
    )
    
    if st.button("Processar Vídeo"):
        if youtube_url:
            try:
                with st.spinner("Baixando e transcrevendo o vídeo..."):
                    audio_path, video_title = download_youtube_audio(youtube_url)
                    
                    if not os.path.exists(audio_path):
                        raise Exception(f"Arquivo de áudio não foi criado corretamente: {audio_path}")
                        
                    audio_chunks = split_audio(audio_path)
                    transcript = ''.join([transcribe_audio(chunk) for chunk in audio_chunks])
                    
                    try:
                        os.remove(audio_path)
                    except Exception as e:
                        st.warning(f"Aviso: Não foi possível remover arquivo temporário: {str(e)}")
                    
                    st.success("Transcrição concluída!")
                    st.write("### Transcrição:")
                    st.text_area("", transcript, height=200)
                    
                    with st.spinner("Gerando estrutura do artigo..."):
                        outline = generate_article_outline(transcript)
                        st.write("### Estrutura do Artigo:")
                        st.text_area("", outline, height=200)
                    
                    with st.spinner("Escrevendo primeira versão do artigo..."):
                        initial_article = write_full_article(transcript, outline)
                        st.write("### Primeira Versão do Artigo:")
                        st.text_area("", initial_article, height=400)

                    with st.spinner("Revisando artigo..."):
                        review_feedback = review_article(transcript, initial_article)
                        st.write("### Feedback da Revisão:")
                        st.text_area("", review_feedback, height=200)
                    
                    with st.spinner("Criando versão final do artigo..."):
                        final_article = create_final_version(transcript, initial_article, review_feedback)
                        st.write("### Versão Final do Artigo:")
                        st.text_area("", final_article, height=400)
                    
            except Exception as e:
                st.error(f"Ocorreu um erro: {str(e)}")
        else:
            st.warning("Por favor, insira um URL do YouTube.")

if __name__ == "__main__":
    main()