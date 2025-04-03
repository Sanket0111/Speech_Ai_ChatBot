# Speech AI Internship Assignment - ShopOut

This project is a submission for the Speech AI Internship assignment at ShopOut. It implements a complete pipeline for processing YouTube videos through transcription, translation, and creating an interactive chatbot system with regional language support.

## Assignment Requirements

The assignment required the following components:

1. **Transcription Module**: Transcribe English YouTube videos with Indian accent using Google STT or similar services
2. **Translation Module**: Convert transcripts to regional Indian languages
3. **Chatbot**: Build a retrieval-based QA system for the translated content
4. **Bonus**: Implement a Text-to-Speech conversion system

## Deliverables

### Step 1: YouTube Transcription
- **File**: `app/transcribe_video.py` 
- **Output**: JSON transcript with timestamps (`app/data/transcript.json`)
- **Implementation**: Uses Google Speech-to-Text API with Gemini fallback
- **Features**: Handles video download, audio extraction, and accurate transcription with timestamps

### Step 2: Translation
- **File**: `app/translate_transcript.py`
- **Output**: Translated JSON file (`app/data/translated.json`)
- **Implementation**: Uses Google Translate API for accurate translations
- **Features**: Supports multiple Indian languages (Hindi, Tamil, Telugu, etc.)

### Step 3: Chatbot
- **File**: `app/chatbot.py`
- **Implementation**: Uses Gemini API with context from translations
- **Features**: Stores embeddings in FAISS vector store, maintains conversation history

### Bonus: Text-to-Speech
- **File**: `app/text_to_speech.py`
- **Output**: MP3 audio file (`app/data/output_audio.mp3`)
- **Implementation**: Uses gTTS for synthesizing speech in regional languages
- **Features**: Generates natural-sounding speech with appropriate pauses

## Setup Instructions

### Quick Start
**Windows:**
```
run.bat
```

**Mac/Linux:**
```
chmod +x run.sh
./run.sh
```

### Manual Setup
1. Create a virtual environment:
   ```
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the Gemini API key in `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. Launch the application:
   ```
   python -m streamlit run app/app.py
   ```

## Using the Application

The Streamlit interface provides a user-friendly way to interact with all components:

1. **Transcribe**: Enter a YouTube URL to transcribe the audio
2. **Translate**: Select a language and translate the transcript
3. **Chatbot**: Ask questions about the translated content
4. **Text-to-Speech**: Generate spoken audio of the translations

## Technical Implementation

### Components Used
- **Google Speech-to-Text API**: Accurate transcription with timestamp support
- **Google Translate API**: High-quality translation for Indian languages
- **Google Gemini**: Powers the conversational AI capabilities
- **FAISS**: Vector database for efficient retrieval
- **Streamlit**: Web interface framework
- **yt-dlp**: Reliable YouTube download functionality
- **gTTS**: Text-to-speech conversion for multiple languages

### Project Structure
```
app/
  ├── data/                    # Storage for JSON and audio files
  ├── transcribe_video.py      # Transcription functionality
  ├── translate_transcript.py  # Translation functionality
  ├── chatbot.py               # Chatbot implementation
  ├── text_to_speech.py        # TTS conversion
  └── app.py                   # Streamlit UI
```

## Future Enhancements

Potential improvements that could be implemented:
- Support for more video platforms beyond YouTube
- Improved handling of long-form content
- Enhanced vector search for more precise question answering
- Support for code-mixed language content
- Multi-turn dialogue optimization

## Requirements

- Python 3.8 or higher
- Required Python packages listed in `requirements.txt`
- Internet connection for API access 