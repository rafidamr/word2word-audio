import io
import logging
import librosa
import yaml
import soundfile as sf

from pathlib import Path
from protosa.speech.audio_pb2 import Audio

from app.settings.base import SynthSettings
from prosa_rvc_inference import RVCConverter

import time

synth_settings = SynthSettings()

LOG = logging.getLogger(__name__)


def postprocess_audio(wav_data, sample_freq) -> bytes:
    """Convert wav_data to array of bytes"""
    bytes_io = io.BytesIO(bytes())
    sf.write(bytes_io, wav_data, samplerate=sample_freq, subtype="PCM_16", format="RAW")
    return bytes_io.getbuffer().tobytes()


class ConversionError(Exception):
    pass


class RVCSynthesizer:
    def __init__(self, conf_path):
        with open(conf_path, "r") as conf:
            self.conf_data = yaml.load(conf, Loader=yaml.FullLoader)

        self.target_sr = synth_settings.target_sr
        self.model_root_path = self.conf_data["model_root_path"]
        self.rvc = RVCConverter(
            device=synth_settings.torch_device, n_cpu=synth_settings.n_cpu
        )
        self.rvc.load_model(self.conf_data["model_paths"])
        self.count = 0
        self.cur_speaker = None

    def synthesize(
        self, pitch: float, audio_target: Audio, speaker: str, audio_id: str
    ) -> Audio:
        try:
            # if self.cur_speaker and self.cur_speaker != speaker:
            #     self.rvc.unload_model(self.cur_speaker)
            # self.cur_speaker = speaker

            if speaker not in self.rvc.list_available_models():
                self.rvc.load_model(f"{self.model_root_path}/{speaker}")

            info, model_sr, audio_output, is_success = self.rvc.convert_speaker(
                input_audio=audio_target, pitch_offset=pitch, model_id=speaker
            )

            if not is_success:
                raise ConversionError(info)

            LOG.info("Conversion info: %s", info)
            
            if len(audio_output) == 0:
                return Audio(data=b"", samplerate=model_sr)

            audio_bytes = postprocess_audio(audio_output, model_sr)

            if self.count % 100 == 0:
                self.rvc.unload_model(speaker)

            audio = Audio(
                data=audio_bytes,
                samplerate=model_sr,
                length=len(audio_bytes),
                duration=len(audio_output) / model_sr,
            )

            self.count += 1
            return audio
        except ConversionError as err:
            LOG.error("%s: %s", type(err).__name__, err, exc_info=err)
            return audio_target
        except Exception as err:
            LOG.error("%s: %s", type(err).__name__, err, exc_info=err)
            raise
