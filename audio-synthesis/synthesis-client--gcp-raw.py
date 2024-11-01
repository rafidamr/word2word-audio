#!/usr/bin/env python

import asyncio
import io
import logging
import sys
import os
import time

import soundfile as sf
import librosa

from protosa.speech_grpc import (
    Audio,
    SpeechConversionGrpc,
)

FORMAT = "%(levelname)s %(asctime)-15s %(module)s.%(funcName)s:%(lineno)s :\
 %(message)s"

log = logging.getLogger(__name__)



def postprocess_audio(wav_data, sample_freq) -> bytes:
    """Convert wav_data to array of bytes"""
    bytes_io = io.BytesIO(bytes())
    sf.write(bytes_io, wav_data, samplerate=sample_freq, subtype="PCM_16", format="RAW")
    return bytes_io.getbuffer().tobytes()


async def synthesize():
    RVC_URI = "127.1:50002"
    SOURCE_LANG = "ar"
    TARGET_LANG = "en"

    # speakers = ["1", "2", "3", "4", "5", "6", "8"]
    speakers = ["0"]

    sc_q = asyncio.Queue()

    RVC_NUM_CLIENT = 10
    for _ in range(RVC_NUM_CLIENT):
        sc_c = SpeechConversionGrpc(RVC_URI, None)
        sc_q.put_nowait(sc_c)

    count = 0
    for s_id in speakers:
        raw_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{s_id}/wav-synthesis/{SOURCE_LANG}-to-{TARGET_LANG}_gcp_raw"
        raws = [os.path.join(raw_folder, f) for f in os.listdir(raw_folder) if f.endswith('.wav')]

        output_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{s_id}/wav-synthesis/{SOURCE_LANG}-to-{TARGET_LANG}"
        os.makedirs(output_folder, exist_ok=True)

        while raws:
            path = raws.pop()
            sc = None
            try:
                audio_input, sr = librosa.load(path, sr=None)
                audio_bytes = postprocess_audio(audio_input, sr)

                sc = sc_q.get_nowait()
                response = await sc.call(
                    speaker_name=s_id,
                    audio=Audio(data=audio_bytes, samplerate=sr),
                    pitch_offset=0,
                )
                audio = response.audio

                filename = os.path.basename(path).replace(".wav", "")
                output_path = f"{output_folder}/{filename}.wav"
                with sf.SoundFile(
                    output_path,
                    mode="w",
                    samplerate=int(audio.samplerate),
                    channels=int(audio.channels),
                    subtype=audio.subtype,
                    format=audio.format,
                ) as f:
                    f.buffer_write(audio.data, "int16")
                
                print(f"Success: s_id={s_id} {filename}.wav")

                count += 1
                if count % 100 == 0:
                    time.sleep(3)
                elif count % 50 == 0:
                    time.sleep(1)
                else:
                    time.sleep(0.05)
            except:
                raws.append(path)
                with open("./retried-synthesis--gcp-raw.txt", mode='a') as f:
                    f.write(f'{path}\n')
                time.sleep(3)
            finally:
                if sc:
                    sc_q.put_nowait(sc)

    print("-" * 100)
    print("Done.")


async def main():
    try:
        test_function = getattr(sys.modules[__name__], "synthesize")
    except AttributeError as e:
        print(e)
        sys.exit()

    tests = [
        asyncio.ensure_future(test_function())
    ]
    done, pending = await asyncio.wait(tests, return_when="FIRST_EXCEPTION")
    if len(pending) > 0:
        for task in pending:
            task.cancel()
        exceptions = [t.exception() for t in done if t.exception()]
        log.info(exceptions)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    asyncio.run(main())
