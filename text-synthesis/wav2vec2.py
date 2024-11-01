import os                                                                                                                   
import torch                                                                                                                
import librosa                                                                                                              
import noisereduce as nr                                                                                                    
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor                                                            
from pyctcdecode import build_ctcdecoder                                                                                    
                                                                                                                            
MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-arabic"                                                                   
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")                                                       
                                                                                                                            
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)                                                                     
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID).to(device)

# Path to folder containing audio files
audio_path = "/home/rafid_tijarah/downloads/audio-raw/infer-diarizer/speaker_output_12h_pt1/SPEAKER_02/0.wav"

# Function to load and denoise audio
def speech_file_to_array_fn(audio_path):
    speech_array, sampling_rate = librosa.load(audio_path, sr=16_000)
    speech_array = nr.reduce_noise(y=speech_array, sr=sampling_rate)  # Apply denoising
    speech_array = librosa.util.normalize(speech_array)
    # speech_array = librosa.effects.pitch_shift(speech_array, sr=sampling_rate, n_steps=1)
    return speech_array

# Preprocess the audio data
speech_arrays = [speech_file_to_array_fn(audio_path)]
inputs = processor(speech_arrays, sampling_rate=16_000, return_tensors="pt", padding=True)
inputs = {key: val.to(device) for key, val in inputs.items()}  # Move inputs to GPU

# Perform inference
with torch.no_grad():
    logits = model(inputs["input_values"], attention_mask=inputs["attention_mask"]).logits

# Decode with greedy decoding
predicted_ids = torch.argmax(logits, dim=-1)
predicted_sentences = processor.batch_decode(predicted_ids, skip_special_tokens=True)

# Using a language model for post-processing with pyctcdecode (Beam Search)
vocab_list = processor.tokenizer.convert_ids_to_tokens(range(processor.tokenizer.vocab_size))
decoder = build_ctcdecoder(vocab_list)
lm_decoded_sentences = [decoder.decode(logit.cpu().numpy()) for logit in logits]

# Print results
for i, (greedy_transcription, lm_transcription) in enumerate(zip(predicted_sentences, lm_decoded_sentences)):
    print(f"Audio file: {audio_path}")
    print(f"Greedy transcription: {greedy_transcription}")
    print(f"LM-decoded transcription: {lm_transcription}")  # Beam search with language model
    print("-" * 100)