# Speech AI Internship Assignment - My Approach

Hey there! This document outlines how I tackled the internship assignment and walks through my solutions for each requirement. I've included some notes on challenges I faced and design decisions I made along the way.

## Project Overview

The assignment asked me to build a pipeline that:
1. Transcribes YouTube videos
2. Translates the content to an Indian language
3. Creates a chatbot for the translated content
4. Converts text back to speech (bonus task)

Here's what I came up with for each part:

## Deliverable 1: YouTube Transcription
**File:** `app/transcribe_video.py`

The first challenge was reliable YouTube downloads. I started with pytube, but it kept breaking with Google's frequent API changes. I switched to yt-dlp which is much more robust and handles various formats better.

For transcription, I initially tried using OpenAI's Whisper, but ran into token limits and pricing issues. Google's Speech-to-Text API turned out to be more reliable and gave better timestamp accuracy. I included a fallback to Gemini's transcription capabilities for cases where Speech-to-Text fails.

Some interesting issues I solved:
- Breaking speech into natural segments based on pauses
- Handling large files by compressing and chunking audio
- Proper error handling for when the YouTube download fails

**To run this part independently:**
```bash
python app/transcribe_video.py --url "https://www.youtube.com/watch?v=YOUTUBE_ID" --model base
```

The output is saved as `app/data/transcript.json` with timestamps for each segment.

## Deliverable 2: Translation
**File:** `app/translate_transcript.py`

Google Translate was the obvious choice here, but I had to be careful about rate limits. The free tier only allows a certain number of characters per request, so I implemented batch processing with error handling.

I made sure to preserve the original English text alongside the translations and maintain all the timestamps. This was important for the later audio generation step.

For this assignment, I focused on Hindi, but the code supports all major Indian languages:
- Hindi, Bengali, Telugu, Tamil
- Marathi, Gujarati, Kannada, Malayalam
- Punjabi, Urdu, Odia, Assamese

**To run this part independently:**
```bash
python app/translate_transcript.py --language hindi --input app/data/transcript.json
```

Output is saved as `app/data/translated.json`.

## Deliverable 3: Chatbot Implementation
**File:** `app/chatbot.py`

This was the most challenging part. I initially tried using a sophisticated vector retrieval approach with embeddings, but kept running into dependency conflicts and token limit issues. After spending way too much time debugging, I simplified to a more reliable approach using Gemini's API directly.

The chatbot:
- Loads the translated content (maintains context of both languages)
- Uses Gemini to answer questions about the content
- Stores conversation history for context
- Creates a FAISS index of embeddings for potential future improvements

I had to carefully tune the prompts to get Gemini to answer based on the content rather than making things up. The chat history feature helps maintain context across multiple questions.

**To run this part independently:**
```bash
python app/chatbot.py --file app/data/translated.json
```

Conversations are saved to `app/data/chatbot_interactions.json` and the vector store is in `app/data/faiss_index/`.

## Bonus Deliverable: Text-to-Speech
**File:** `app/text_to_speech.py`

Since Google's TTS API can get expensive, I used gTTS which works surprisingly well for many Indian languages. The challenge here was managing the audio segments and ensuring natural flow:

- Each translated segment is converted to speech
- Short pauses are added between segments
- All the pieces are concatenated to a single MP3

One quirk I noticed: gTTS pronunciation for some Indian languages is better than others. Hindi and Tamil work really well, but some of the less common languages could use improvement.

**To run this part independently:**
```bash
python app/text_to_speech.py --input app/data/translated.json
```

The output audio file is saved as `app/data/output_audio.mp3`.

## Full Application Integration

All of these components are tied together in a clean Streamlit interface (`app/app.py`). You can run the full application with:

```bash
python -m streamlit run app/app.py
```

## Development Notes

A few things I learned during this process:
1. API reliability is crucial - always have fallbacks
2. Token limits and API costs add up quickly
3. Error handling is not optional
4. Threading would help with the translation batching speed
5. The Streamlit UI simplified a lot of the interaction complexity

## Cleanup & Organization

You might notice some duplicate files in the repo. This happened because I was iteratively improving the code and wanted to keep backups as I went:
- `transcribe.py` vs `transcribe_video.py` 
- `translate.py` vs `translate_transcript.py`

I kept the original modules working while developing the assignment-specific versions to avoid breaking existing functionality. The app automatically selects the best available version.

If you have any questions about my implementation or want to discuss specific technical details, I'd be happy to chat! 