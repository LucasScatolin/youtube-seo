# YouTube to SEO Article Generator

This Streamlit application automatically generates SEO-optimized articles from YouTube videos. It transcribes the video content and uses AI to create well-structured, informative articles in Brazilian Portuguese.

## Features

- YouTube video audio extraction
- Audio transcription using OpenAI's Whisper
- SEO-optimized article structure generation
- Multi-step article creation process:
  - Initial draft generation
  - Technical review
  - Final version with corrections
- Minimum 600-word articles
- Full error handling and progress tracking

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- OpenAI API key
- Git (for deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/youtube-to-seo-article.git
cd youtube-to-seo-article
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Install system dependencies:
```bash
# On Ubuntu/Debian
sudo apt-get update && sudo apt-get install ffmpeg

# On macOS
brew install ffmpeg

# On Windows
# Download and install FFmpeg from https://ffmpeg.org/download.html
```

## Configuration

1. Create a `.env` file in the project root (for local development):
```bash
OPENAI_API_KEY=your-api-key-here
```

2. For Streamlit Cloud deployment, create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

## Local Development

Run the app locally:
```bash
streamlit run app.py
```

## Deployment

1. Create a GitHub repository and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/your-repo-name.git
git push -u origin main
```

2. Deploy on Streamlit Cloud:
- Visit [share.streamlit.io](https://share.streamlit.io)
- Connect your GitHub account
- Select your repository
- Add your OpenAI API key in the secrets management section

## Usage

1. Launch the application
2. Paste a YouTube URL in the input field
3. Click "Processar Vídeo"
4. The app will:
   - Download and transcribe the video
   - Generate an article outline
   - Create an initial draft
   - Perform a technical review
   - Generate a final, corrected version

## Project Structure

```
project/
├── .streamlit/
│   └── secrets.toml
├── app.py
├── requirements.txt
├── packages.txt
├── .gitignore
└── README.md
```

## Required Files

### requirements.txt
```
streamlit
openai
python-dotenv
pydub
yt-dlp
ffmpeg-python
```

### packages.txt
```
ffmpeg
```

### .gitignore
```
.env
__pycache__/
*.pyc
.idea/
.vscode/
*.wav
temp/
.streamlit/secrets.toml
```

## Environment Variables

The application requires the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key

## Error Handling

The application includes comprehensive error handling for:
- Invalid YouTube URLs
- Failed downloads
- Transcription errors
- API failures
- File system issues

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the API services
- Streamlit for the web application framework
- yt-dlp for YouTube video processing
- The FFmpeg team for audio processing capabilities