## Computing Power Specification
For translating audio with RTF approximately 1.0 to 1.5 (tested on 12 hours audio):
* GCP Compute Engine 
* L4 GPU (24 GB VRAM) with Nvidia Driver 550, CUDA Toolkit 12.4, and cuDNN 9.5.0 
* 4 CPU cores (8 vCPUs) 
* 32 GB RAM 
* 100-200 GB SSD Persistent Disk

## Common Inference Workflow
> The workflow is basically diarization, ASR, translation, TTS, and voice conversion; proper directory structure is necessary for organizing each speaker text/audio

### Diarization
* Use `diarizer.py`

### Text Synthesis
* Use local ASR `wav2vec2` or ASR API `google_stt.py`
* Remove clutters in the resulting texts
* Use translation API `google_translate_v3.py`

### Audio Synthesis
#### Preprocessing
* If any, remove remaining clutters in the texts
* Instantiate local Voice Conversion (VC) engine with pre-trained models (training the models is a separate process of voice cloning, use RVC-Project) 
* Assign VC ID for each speaker
#### Synthesis
* Indonesian audio synthesis: Spin up a local TTS synthesizer and run `synthesis-client.py`
* English audio synthesis: Use API `google_tts.py` and `synthesis-client--gcp-raw.py`

### Post-processing
* Merge the resulting audios using `merge-audio-gpu.py`
* Upload to the final audio to a storage (drive/bucket/etc)