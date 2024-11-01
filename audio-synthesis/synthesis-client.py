#!/usr/bin/env python

import asyncio
import logging
import sys
import os
import time

import soundfile as sf

from protosa.speech_grpc import (
    Audio,
    SpeechConversionGrpc,
    SpeechSynthesisGrpc,
)

FORMAT = "%(levelname)s %(asctime)-15s %(module)s.%(funcName)s:%(lineno)s :\
 %(message)s"

log = logging.getLogger(__name__)


PITCH_MAP = {
    "0": -1,
    "1": 0,
    "2": -3,
    "3": -3,
    "4": -1,
    "5": -3,
    "6": -1,
    "7": -1,
    "8": -1,
}

async def synthesize():
    NEMO_URI = "127.1:50001"
    RVC_URI = "127.1:50002"
    ATMADJA_ID = 4
    SOURCE_LANG = "ar"
    TARGET_LANG = "id"

    speakers = ["5", "6", "7", "8"]
    # speakers = ["0"]

    ss_q = asyncio.Queue()
    sc_q = asyncio.Queue()

    NEMO_NUM_CLIENT = 5
    RVC_NUM_CLIENT = 5
    for _ in range(NEMO_NUM_CLIENT):
        ss_c = SpeechSynthesisGrpc(NEMO_URI, None)
        ss_q.put_nowait(ss_c)
    for _ in range(RVC_NUM_CLIENT):
        sc_c = SpeechConversionGrpc(RVC_URI, None)
        sc_q.put_nowait(sc_c)

    count = 0
    for s_id in speakers:
        tslation_folder = f"/home/rafid_tijarah/downloads/audio-inference/{s_id}/translation/{SOURCE_LANG}-to-{TARGET_LANG}"
        tslations = [os.path.join(tslation_folder, f) for f in os.listdir(tslation_folder) if f.endswith('.txt')]

        output_folder = f"/home/rafid_tijarah/downloads/audio-inference/{s_id}/wav-synthesis/{SOURCE_LANG}-to-{TARGET_LANG}"
        os.makedirs(output_folder, exist_ok=True)

        while tslations:
            path = tslations.pop()
            ss = None
            sc = None
            try:
                with open(path, mode='r') as f:
                    text = f.read()

                ss = ss_q.get_nowait()
                audio = await ss.call(
                    speaker_id=ATMADJA_ID,
                    text=text,
                    pitch=PITCH_MAP[s_id]
                )

                sc = sc_q.get_nowait()
                response = await sc.call(
                    speaker_name=s_id,
                    audio=Audio(data=audio.data, samplerate=audio.samplerate),
                    pitch_offset=0,
                )
                audio = response.audio

                filename = os.path.basename(path).replace(".txt", "")
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
                tslations.append(path)
                time.sleep(3)
            finally:
                if ss:
                    ss_q.put_nowait(ss)
                if sc:
                    sc_q.put_nowait(sc)


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
