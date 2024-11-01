import os
import librosa
import soundfile as sf
import numpy as np
import torch


synthesis_speakers = ["1", "2", "3", "4", "5", "6", "7", "8"]
# synthesis_speakers = ["2"]

PART = "1"
SOURCE_LANG = "ar"
TARGET_LANG = "id"

output_folder = f"/home/rafid_tijarah/audio-final--gcp-stt/{SOURCE_LANG}-to-{TARGET_LANG}"
os.makedirs(output_folder, exist_ok=True)

final_filename = f"{output_folder}/{SOURCE_LANG}-{TARGET_LANG}_{PART}.wav"

target_sr = 48_000

merged_audio = torch.tensor([]).to("cuda")
synthesized_files = dict()
ori_files = []



# COLLECT SYNTHESIZED AUDIO FROM EACH SPEAKER
for s_id in synthesis_speakers:
    wav_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{s_id}/wav-synthesis/{SOURCE_LANG}-to-{TARGET_LANG}"
    for f in os.listdir(wav_folder):
        if f.startswith(f'{PART}_'):
            idx = int(f.replace(f'{PART}_', '').replace('.wav', ''))
            path = os.path.join(wav_folder, f)
            synthesized_files[idx] = path



# COLLECT ORI
ori_folder = f"/home/rafid_tijarah/downloads/audio-raw/audio-diarization/speaker_output_12h_pt{PART}"
# ori_folder = f"/home/rafid_tijarah/downloads/audio-temp"
for diarization_speaker in os.listdir(ori_folder):
    s_folder = os.path.join(ori_folder, diarization_speaker)
    arr = [(int(f.replace('.wav', '')), os.path.join(s_folder, f)) for f in os.listdir(s_folder)]
    ori_files.extend(arr)

# SORT ORI AUDIO
ori_files.sort(key=lambda el: el[0])



# MERGE ALL AUDIO
for f, p in ori_files:
    audio, _ = librosa.load(p, sr=target_sr)
    audio_tensor = torch.from_numpy(audio).to("cuda")
    merged_audio = torch.cat((merged_audio, audio_tensor))
    print(f"Merged: {p}")
    if f in synthesized_files:
        audio, _ = librosa.load(synthesized_files[f], sr=target_sr)
        audio_tensor = torch.from_numpy(audio).to("cuda")
        merged_audio = torch.cat((merged_audio, audio_tensor))
        print(f"Merged: {synthesized_files[f]}")

final_audio = merged_audio.cpu().numpy()

sf.write(
    final_filename,
    final_audio,
    target_sr
)
print("Audio files have been merged")
