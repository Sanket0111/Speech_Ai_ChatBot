#!/usr/bin/env python3
"""
Translate transcript from English to a regional Indian language.
Saves the translated text in a JSON file.

Assignment Deliverable: Step 2
"""

import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from googletrans import Translator

# Load environment variables
load_dotenv()

# Language code mapping for Indian languages
LANGUAGE_CODES = {
    "hindi": "hi",
    "bengali": "bn",
    "telugu": "te",
    "marathi": "mr",
    "tamil": "ta",
    "urdu": "ur",
    "gujarati": "gu",
    "kannada": "kn",
    "odia": "or",
    "punjabi": "pa",
    "malayalam": "ml",
    "assamese": "as"
}

def load_transcript(transcript_file):
    """Load transcript from JSON file."""
    try:
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript = json.load(f)
        return transcript
    except Exception as e:
        print(f"Error loading transcript: {e}")
        return None

def translate_text(text, target_language):
    """
    Translate text to target language using Google Translate API.
    """
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Error with translation API: {e}")
        # Fall back to a simple indicator if API fails
        return f"{text} [Translation Error]"

def translate_transcript(transcript, target_language):
    """Translate entire transcript to target language."""
    print(f"Translating transcript to {target_language}...")
    
    # Create a translated copy of the transcript
    translated = {
        "title": transcript["title"],
        "target_language": target_language,
        "segments": []
    }
    
    # Initialize translator
    translator = Translator()
    
    # Translate each segment
    total_segments = len(transcript["segments"])
    for i, segment in enumerate(transcript["segments"]):
        if i % 5 == 0:
            print(f"Translating segment {i+1}/{total_segments}")
        
        try:
            # Translate in batches to avoid API limits
            translated_text = translator.translate(segment["text"], dest=target_language).text
        except Exception as e:
            print(f"Error translating segment {i+1}: {e}")
            translated_text = f"[Translation error: {str(e)[:50]}...]"
        
        translated["segments"].append({
            "start": segment["start"],
            "end": segment["end"],
            "original": segment["text"],
            "translated": translated_text
        })
    
    print("Translation completed!")
    return translated

def save_translation(translated, target_language, output_dir="app/data"):
    """Save translated transcript as JSON file."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Clean the title to create a valid filename
        safe_title = "".join(c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in translated["title"])
        safe_title = safe_title.strip().replace(' ', '_')
        
        # Save to JSON file
        output_file = os.path.join(output_dir, f"translated_{target_language}_{safe_title}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated, f, ensure_ascii=False, indent=2)
        
        # Also save as translated.json for assignment submission
        translated_json = os.path.join(output_dir, "translated.json")
        with open(translated_json, 'w', encoding='utf-8') as f:
            json.dump(translated, f, ensure_ascii=False, indent=2)
            
        print(f"Translation saved to: {output_file}")
        print(f"Assignment deliverable saved as: {translated_json}")
        return output_file
        
    except Exception as e:
        print(f"Error saving translation: {e}")
        return None

def main():
    """Main function to translate a transcript."""
    parser = argparse.ArgumentParser(description="Translate transcript to a regional Indian language.")
    parser.add_argument("--input", type=str, help="Input transcript JSON file")
    parser.add_argument("--language", type=str, required=True, choices=list(LANGUAGE_CODES.keys()),
                        help="Target language for translation")
    parser.add_argument("--output", type=str, default="app/data", help="Output directory for translated file")
    
    args = parser.parse_args()
    
    # If input file not provided, use the most recent transcript in data folder
    if args.input is None:
        data_dir = Path("app/data")
        transcripts = list(data_dir.glob("transcript_*.json"))
        if not transcripts:
            print("No transcript files found in data directory.")
            return
        
        # Sort by modification time, newest first
        transcripts.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        args.input = str(transcripts[0])
        print(f"Using most recent transcript: {args.input}")
    
    # Load transcript
    transcript = load_transcript(args.input)
    
    if transcript:
        # Translate transcript
        target_language_code = LANGUAGE_CODES[args.language]
        translated = translate_transcript(transcript, target_language_code)
        
        if translated:
            # Save translation to JSON
            output_file = save_translation(translated, args.language, args.output)
            
            if output_file:
                print(f"Successfully translated transcript to {args.language} and saved to {output_file}")
                return output_file
    
    print("Translation process failed.")
    return None

if __name__ == "__main__":
    main() 