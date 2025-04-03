#!/usr/bin/env python3
"""
Main Streamlit application for Speech AI System.
Combines transcription, translation, and chatbot functionality with Google Gemini.
"""

import os
import json
import tempfile
import streamlit as st
from pathlib import Path
import sys
import importlib.util
import google.generativeai as genai

# Add parent directory to path to make imports work from any location
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Centralized API key management
def setup_api_keys():
    """Set up API keys in a centralized location"""
    # Gemini API key
    gemini_api_key = "Add your GEMINI KEY"
    os.environ["GEMINI_API_KEY"] = gemini_api_key
    genai.configure(api_key=gemini_api_key)
    return {
        "gemini_api_key": gemini_api_key
    }

# Set up API keys
API_KEYS = setup_api_keys()

# Dynamic imports to avoid circular imports
def import_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import project modules - using the assignment deliverable files
transcribe = import_module("transcribe_video", os.path.join(current_dir, "transcribe_video.py"))
translate = import_module("translate_transcript", os.path.join(current_dir, "translate_transcript.py"))
chatbot = import_module("chatbot", os.path.join(current_dir, "chatbot.py"))
text_to_speech = import_module("text_to_speech", os.path.join(current_dir, "text_to_speech.py"))

# Set page config
st.set_page_config(
    page_title="Speech AI System",
    page_icon="🎤",
    layout="wide"
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "transcript_file" not in st.session_state:
    st.session_state.transcript_file = None
if "translation_file" not in st.session_state:
    st.session_state.translation_file = None
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

def find_json_files(pattern):
    """Find JSON files matching a pattern."""
    data_dir = Path("app/data")
    json_files = list(data_dir.glob(pattern))
    
    # If no files found in app/data, try looking in data/ (for when running from app dir)
    if not json_files:
        data_dir = Path("data")
        json_files = list(data_dir.glob(pattern))
        
    return json_files

def display_json_content(file_path):
    """Display the content of a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return None

def main():
    """Main Streamlit app."""
    st.title("Speech AI System with Gemini")
    
    # Create a sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Transcribe", "Translate", "Chatbot", "Text-to-Speech"])
    
    # Display API key info
    st.sidebar.info(f"Using Gemini API key: {API_KEYS['gemini_api_key'][:10]}... (pre-configured)")
    
    # Transcription Page
    if page == "Transcribe":
        st.header("Step 1: Transcribe YouTube Video")
        
        # YouTube URL input
        youtube_url = st.text_input("Enter YouTube URL:")
        
        # Model selection
        model_options = ["base", "enhanced"]
        selected_model = st.selectbox("Select transcription model:", model_options, index=0)
        
        # Transcribe button
        if st.button("Transcribe Video"):
            if youtube_url:
                with st.spinner("Downloading and transcribing video..."):
                    # Create progress message
                    progress_placeholder = st.empty()
                    progress_placeholder.text("Downloading audio from YouTube...")
                    
                    # Download audio
                    audio_file, video_title = transcribe.download_youtube_audio(youtube_url)
                    
                    if audio_file and video_title:
                        progress_placeholder.text(f"Transcribing audio with Google Speech-to-Text ({selected_model} model)...")
                        
                        # Transcribe audio
                        segments = transcribe.transcribe_audio(audio_file, selected_model)
                        
                        if segments:
                            progress_placeholder.text("Saving transcript...")
                            
                            # Save transcript
                            output_file = transcribe.save_transcript(segments, video_title)
                            
                            if output_file:
                                st.session_state.transcript_file = output_file
                                progress_placeholder.text("")
                                st.success(f"Transcription completed! Saved to: {output_file}")
                            else:
                                st.error("Failed to save transcript.")
                        else:
                            st.error("Transcription failed.")
                    else:
                        st.error("Failed to download YouTube video.")
            else:
                st.warning("Please enter a YouTube URL.")
        
        # Display existing transcripts
        st.subheader("Existing Transcripts")
        transcript_files = find_json_files("transcript_*.json")
        
        if transcript_files:
            selected_transcript = st.selectbox(
                "Select a transcript:", 
                transcript_files,
                format_func=lambda x: x.name
            )
            
            if selected_transcript:
                st.session_state.transcript_file = str(selected_transcript)
                transcript_data = display_json_content(selected_transcript)
                
                if transcript_data:
                    st.subheader(f"Transcript: {transcript_data.get('title', 'Unknown')}")
                    
                    # Display segments
                    for i, segment in enumerate(transcript_data.get("segments", [])):
                        if i < 10:  # Limit display to first 10 segments
                            st.text(f"[{segment.get('start', 0):.2f}s - {segment.get('end', 0):.2f}s]: {segment.get('text', '')}")
                        elif i == 10:
                            st.text("... (more segments)")
                            break
        else:
            st.info("No transcripts found. Transcribe a video first.")
    
    # Translation Page
    elif page == "Translate":
        st.header("Step 2: Translate Transcript")
        
        # Language selection
        language_options = list(translate.LANGUAGE_CODES.keys())
        selected_language = st.selectbox("Select target language:", language_options)
        
        # Input transcript selection
        transcript_files = find_json_files("transcript_*.json")
        
        if transcript_files:
            selected_transcript = st.selectbox(
                "Select a transcript to translate:", 
                transcript_files,
                format_func=lambda x: x.name
            )
            
            # Translate button
            if st.button("Translate Transcript"):
                if selected_transcript:
                    with st.spinner(f"Translating transcript to {selected_language}..."):
                        # Load transcript
                        transcript = translate.load_transcript(selected_transcript)
                        
                        if transcript:
                            # Translate transcript
                            target_language_code = translate.LANGUAGE_CODES[selected_language]
                            translated = translate.translate_transcript(transcript, target_language_code)
                            
                            if translated:
                                # Save translation
                                output_file = translate.save_translation(translated, selected_language)
                                
                                if output_file:
                                    st.session_state.translation_file = output_file
                                    st.success(f"Translation completed! Saved to: {output_file}")
                                else:
                                    st.error("Failed to save translation.")
                            else:
                                st.error("Translation failed.")
                        else:
                            st.error("Failed to load transcript.")
                else:
                    st.warning("Please select a transcript to translate.")
        else:
            st.info("No transcripts found. Please transcribe a video first.")
        
        # Display existing translations
        st.subheader("Existing Translations")
        translation_files = find_json_files("translated_*.json")
        
        if translation_files:
            selected_translation = st.selectbox(
                "Select a translation:", 
                translation_files,
                format_func=lambda x: x.name
            )
            
            if selected_translation:
                st.session_state.translation_file = str(selected_translation)
                translation_data = display_json_content(selected_translation)
                
                if translation_data:
                    st.subheader(f"Translation: {translation_data.get('title', 'Unknown')}")
                    st.text(f"Language: {translation_data.get('target_language', 'Unknown')}")
                    
                    # Display segments with original and translated text
                    for i, segment in enumerate(translation_data.get("segments", [])):
                        if i < 5:  # Limit display to first 5 segments
                            st.markdown(f"**Original**: {segment.get('original', '')}")
                            st.markdown(f"**Translated**: {segment.get('translated', '')}")
                            st.text("---")
                        elif i == 5:
                            st.text("... (more segments)")
                            break
        else:
            st.info("No translations found. Translate a transcript first.")
    
    # Chatbot Page
    elif page == "Chatbot":
        st.header("Step 3: Chat with Translated Content")
        
        # Initialize or load chatbot
        if st.session_state.chatbot is None:
            # Input translation selection
            translation_files = find_json_files("translated_*.json")
            
            if translation_files:
                selected_translation = st.selectbox(
                    "Select a translation for chatbot:", 
                    translation_files,
                    format_func=lambda x: x.name
                )
                
                # Initialize chatbot button
                if st.button("Initialize Chatbot"):
                    with st.spinner("Initializing chatbot..."):
                        st.session_state.chatbot = chatbot.TranslationChatbot(
                            selected_translation, 
                            True  # Always use Gemini
                        )
                        st.success("Chatbot initialized! You can start chatting now.")
            else:
                st.info("No translations found. Please translate a transcript first.")
        
        # Chat interface
        if st.session_state.chatbot:
            st.subheader("Chat")
            
            # Display chat history from chatbot instance
            for message in st.session_state.chatbot.chat_history:
                if message["role"] == "user":
                    st.markdown(f"**You**: {message['content']}")
                else:
                    st.markdown(f"**Assistant**: {message['content']}")
            
            # User input
            user_input = st.text_input("Ask a question about the translated content:")
            
            if st.button("Send") and user_input:
                # Get response from chatbot
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.query(user_input)
                
                # Rerun to update the chat display
                st.rerun()
            
            # Reset chat button
            if st.button("Reset Chat"):
                st.session_state.chatbot.chat_history = []
                st.rerun()
    
    # Text-to-Speech Page
    elif page == "Text-to-Speech":
        st.header("Bonus: Text-to-Speech Conversion")
        
        # Input translation selection
        translation_files = find_json_files("translated_*.json")
        
        if translation_files:
            selected_translation = st.selectbox(
                "Select a translation for TTS:", 
                translation_files,
                format_func=lambda x: x.name
            )
            
            # Load translation
            translation_data = None
            if selected_translation:
                translation_data = display_json_content(selected_translation)
            
            if translation_data:
                # Get language
                target_language = translation_data.get("target_language")
                
                # Convert to speech button
                if st.button("Generate Speech"):
                    with st.spinner("Generating speech..."):
                        output_file = text_to_speech.concatenate_audio_segments(
                            translation_data, 
                            target_language
                        )
                        
                        if output_file:
                            st.session_state.audio_file = output_file
                            st.success(f"Speech generated! Saved to: {output_file}")
                        else:
                            st.error("Failed to generate speech.")
        else:
            st.info("No translations found. Please translate a transcript first.")
        
        # Display existing audio files
        st.subheader("Generated Audio Files")
        audio_files = list(Path("app/data").glob("speech_*.mp3"))
        
        if audio_files:
            selected_audio = st.selectbox(
                "Select an audio file to play:", 
                audio_files,
                format_func=lambda x: x.name
            )
            
            if selected_audio:
                st.session_state.audio_file = str(selected_audio)
                # Convert Path object to string for st.audio()
                st.audio(str(selected_audio))
        else:
            st.info("No audio files found. Generate speech first.")

if __name__ == "__main__":
    main() 
