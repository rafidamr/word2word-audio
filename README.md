## Common Workflow

### Diarization
* diarizer.py

### Text Synthesis
* google_stt.py
    * remove clutters
* google_translate_v3.py

### Audio Synthesis
#### Preprocessing
* remove clutters
* assign rvc id for each speaker
#### Synthesis
* synthesis-client.py: ar-id, en-id
* google_tts.py & synthesis-client--gcp-raw.py: ar-en

### Post-processing
* merge-audio-gpu.py
* upload to storage