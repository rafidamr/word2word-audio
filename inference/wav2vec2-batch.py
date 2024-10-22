import os
import torch
import librosa
import noisereduce as nr
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from pyctcdecode import build_ctcdecoder


speakers = ["2", "3", "4", "5", "6", "7", "8"]

for speaker_id in speakers:
    BATCH_SIZE = 25
    MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-arabic"
    device = torch.device("cuda")

    # Path to folder containing audio files
    audio_folder = f"/home/rafid_tijarah/downloads/audio-inference/{speaker_id}/wav-source"
    audio_files = [os.path.join(audio_folder, f) for f in os.listdir(audio_folder) if f.endswith('.wav')]

    output_folder = f"/home/rafid_tijarah/downloads/audio-inference/{speaker_id}/transcript"
    os.makedirs(output_folder, exist_ok=True)

    # Function to load and denoise audio
    def speech_file_to_array_fn(audio_path):
        speech_array, sampling_rate = librosa.load(audio_path, sr=16_000)
        speech_array = nr.reduce_noise(y=speech_array, sr=sampling_rate)  # Apply denoising
        speech_array = librosa.util.normalize(speech_array)
        return speech_array

    # Preprocess the audio data
    speech_arrays = [speech_file_to_array_fn(audio_path) for audio_path in audio_files]

    for lower_bound in range(0, len(speech_arrays), BATCH_SIZE):
        processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
        model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID).to(device)

        inputs = processor(speech_arrays[lower_bound:lower_bound+BATCH_SIZE], sampling_rate=16_000, return_tensors="pt", padding=True)
        inputs = {key: val.to(device) for key, val in inputs.items()}  # Move inputs to GPU

        # Perform inference
        with torch.no_grad():
            logits = model(inputs["input_values"], attention_mask=inputs["attention_mask"]).logits

        # Using a language model for post-processing with pyctcdecode (Beam Search)
        vocab_list = processor.tokenizer.convert_ids_to_tokens(range(processor.tokenizer.vocab_size))
        decoder = build_ctcdecoder(vocab_list)
        decoded_sentences = [decoder.decode(logit.cpu().numpy()) for logit in logits]

        # Print results
        for i, transcription in enumerate(decoded_sentences):
            audio_filename = os.path.basename(audio_files[lower_bound + i]).replace(".wav", "")
            transcription_filename = os.path.join(output_folder, f"{audio_filename}.txt")

            with open(transcription_filename, mode='w') as obj:
                obj.write(transcription)

            print(f"Finished transcription: {audio_filename}")

        del processor
        del model
        keys = [k for k in inputs.keys()]
        for k in keys:
            del inputs[k]
        torch.cuda.empty_cache()