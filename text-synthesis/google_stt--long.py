import os
import librosa
import soundfile as sf
import io
from google.cloud import speech

# Set up the Speech client
client = speech.SpeechClient()

sample_rate = 48_000

def postprocess_audio(wav_data, sample_freq) -> bytes:
    """Convert wav_data to array of bytes"""
    bytes_io = io.BytesIO(bytes())
    sf.write(bytes_io, wav_data, samplerate=sample_freq, subtype="PCM_16", format="RAW")
    return bytes_io.getbuffer().tobytes()

# Function to transcribe audio
def transcribe_audio(gcs_uri):
    # Configure audio and recognition settings
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="ar",  # Replace with appropriate language code
        sample_rate_hertz=sample_rate,
    )
    
    # Transcribe the audio file
    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)
    
    # Collect the transcription results
    transcription = "\n".join(result.alternatives[0].transcript for result in response.results)
    return transcription



speakers = ["5"]

for speaker_id in speakers:
    # audio_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{speaker_id}/wav-source"
    output_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{speaker_id}/transcript"
    # os.makedirs(output_folder, exist_ok=True)

    urls = [
        "gs://hadith-project/temp/2_1910.wav",
        "gs://hadith-project/temp/2_1941.wav",
        "gs://hadith-project/temp/2_1906.wav",
        "gs://hadith-project/temp/3_1713.wav",
        "gs://hadith-project/temp/3_151.wav"
    ]

    for gcs_url in urls:
        # Perform transcription
        transcription = transcribe_audio(gcs_url)
        filename = os.path.basename(gcs_url)

        # Save transcription to file
        output_path = os.path.join(output_folder, f"{filename.replace('.wav','')}.txt")
        with open(output_path, "w") as output_file:
            output_file.write(transcription)
        
        print(f"Transcription for {filename} saved to {output_path}")

