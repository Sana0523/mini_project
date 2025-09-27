import pyaudio
import wave
import requests
import os

# --- Configuration ---
SAMPLE_RATE = 16000  # Must match the sample rate Whisper was trained on
CHANNELS = 1
CHUNK_SIZE = 1024
RECORD_SECONDS = 5
OUTPUT_FILENAME = "test_audio.wav"
API_URL = "http://127.0.0.1:8000/transcribe/"

def record_audio():
    """Records audio from the microphone for a fixed duration."""
    audio = pyaudio.PyAudio()
    
    print("\n" + "="*50)
    print(f"🎤 Recording for {RECORD_SECONDS} seconds... Please speak clearly.")
    print("="*50)
    
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    frames = []
    for _ in range(0, int(SAMPLE_RATE / CHUNK_SIZE * RECORD_SECONDS)):
        data = stream.read(CHUNK_SIZE)
        frames.append(data)
        
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save the recorded audio to a WAV file
    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
        
    print(f"✅ Recording saved as '{OUTPUT_FILENAME}'")
    return OUTPUT_FILENAME

def send_for_transcription(audio_filename):
    """Sends the audio file to the FastAPI service and prints the response."""
    print(f"\n🚀 Sending '{audio_filename}' to the transcription service at {API_URL}...")
    
    try:
        # Prepare the file for the POST request
        with open(audio_filename, 'rb') as f:
            # CORRECTED: The key here must match the argument name in your FastAPI endpoint.
            # Your server expects 'file', so we send 'file'.
            files = {'file': (audio_filename, f, 'audio/wav')}
            response = requests.post(API_URL, files=files)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*50)
            print("✅ TRANSCRIPTION SUCCESSFUL")
            print("="*50)
            print(f"🗣️ Text: '{result.get('transcription')}'")
            print(f"⏱️ Processing Time: {result.get('processing_time_seconds')} seconds")
        else:
            print(f"❌ Error: Server returned status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR: Could not connect to the server.")
        print("Please make sure your 'stt_service.py' is running in another terminal.")
    finally:
        # Clean up the created audio file
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
            print(f"\n🗑️ Cleaned up temporary file '{audio_filename}'.")

if __name__ == "__main__":
    audio_file = record_audio()
    send_for_transcription(audio_file)

