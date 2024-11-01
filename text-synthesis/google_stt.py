import os
import librosa
import soundfile as sf
import io
from google.cloud import speech

# Set up the Speech client
client = speech.SpeechClient()

sample_rate = 48_000
PART = "1"

def postprocess_audio(wav_data, sample_freq) -> bytes:
    """Convert wav_data to array of bytes"""
    bytes_io = io.BytesIO(bytes())
    sf.write(bytes_io, wav_data, samplerate=sample_freq, subtype="PCM_16", format="RAW")
    return bytes_io.getbuffer().tobytes()

# Function to transcribe audio
def transcribe_audio(audio_path):
    # Load audio file
    audio, _ = librosa.load(audio_path, sr=sample_rate, mono=False)
    mono_audio = librosa.to_mono(audio)
    audio_bytes = postprocess_audio(mono_audio, sample_rate)
    
    # Configure audio and recognition settings
    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="ar",  # Replace with appropriate language code
        sample_rate_hertz=sample_rate,
    )
    
    # Transcribe the audio file
    response = client.recognize(config=config, audio=audio)
    
    # Collect the transcription results
    transcription = "\n".join(result.alternatives[0].transcript for result in response.results)
    return transcription



# speakers = ["0"]
speakers = ["1", "2", "3", "4", "5", "6", "7", "8"]

for speaker_id in speakers:
    audio_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{speaker_id}/wav-source"
    output_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{speaker_id}/transcript"
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(audio_folder):
        if filename.startswith(f"{PART}_") and filename.endswith(".wav"):
            try:
                audio_path = os.path.join(audio_folder, filename)
                print(f"Transcribing {filename}...")
                
                # Perform transcription
                transcription = transcribe_audio(audio_path)
                
                # Save transcription to file
                output_path = os.path.join(output_folder, f"{filename.replace('.wav','')}.txt")
                with open(output_path, "w") as output_file:
                    output_file.write(transcription)
                
                print(f"Transcription for {filename} saved to {output_path}")
            except:
                with open("google_stt--failed.txt", mode="a") as f:
                    f.write(os.path.join(output_folder, filename))
