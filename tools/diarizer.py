from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from pydub import AudioSegment
import torch
import torchaudio
import os


USE_AUTH_TOKEN = os.environ.get("USE_AUTH_TOKEN")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=USE_AUTH_TOKEN)

# send pipeline to GPU (when available)
pipeline.to(torch.device("cuda"))

# Check CUDA and CuDNN
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")
print(f"torch.device('cuda'): {torch.device('cuda')}")
print(f"torch.backends.cudnn.enabled: {torch.backends.cudnn.enabled}")
print(f"torch.backends.cudnn.version(): {torch.backends.cudnn.version()}")

# ====================================================================================

audio_file = "./madinah-12h-pt1.wav"
output_dir = "speaker_output_12h_pt1"
max_speakers = 10

with ProgressHook() as hook:
    # diarization = pipeline(audio_file, hook=hook, max_speakers=max_speakers)
    waveform, sample_rate = torchaudio.load(audio_file)
    diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate}, hook=hook, max_speakers=max_speakers)

# Load the entire audio file using pydub
audio = AudioSegment.from_wav(audio_file)

# Create a folder to store the split audio segments (one for each speaker)
os.makedirs(output_dir, exist_ok=True)

# ====================================================================================

# Loop through the diarization results
for i, (turn, _, speaker) in enumerate(diarization.itertracks(yield_label=True)):
    # Extract the start and end time for each speaker segment
    start_time = turn.start * 1000  # pydub works in milliseconds
    end_time = turn.end * 1000

    # Extract the audio segment corresponding to the current speaker
    speaker_segment = audio[start_time:end_time]

    # Create a folder for each speaker
    speaker_folder = os.path.join(output_dir, speaker)
    os.makedirs(speaker_folder, exist_ok=True)

    # Save the audio segment for each speaker
    speaker_segment.export(f"{speaker_folder}/{i}.wav", format="wav")