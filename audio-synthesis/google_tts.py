import os
from google.cloud import texttospeech


SOURCE_LANG = "ar"
TARGET_LANG = "en"

# speakers = ["1", "2", "3", "4", "5", "6", "8"]
speakers = ["0"]

# Instantiates a client
client = texttospeech.TextToSpeechClient()

for s_id in speakers:
    tslation_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{s_id}/translation/{SOURCE_LANG}-to-{TARGET_LANG}"
    tslations = [os.path.join(tslation_folder, f) for f in os.listdir(tslation_folder) if f.endswith('.txt')]

    output_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{s_id}/wav-synthesis/{SOURCE_LANG}-to-{TARGET_LANG}_gcp_raw"
    os.makedirs(output_folder, exist_ok=True)

    for path in tslations:
        try:
            text_input = None
            with open(path, mode='r') as f:
                text_input = f.read()

            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=text_input)

            # Build the voice request, select the language code ("en-US") and the ssml
            # voice gender ("neutral")
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Wavenet-J",
                ssml_gender=texttospeech.SsmlVoiceGender.MALE
            )

            # Select the type of audio file you want returned
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16
            )

            # Perform the text-to-speech request on the text input with the selected
            # voice parameters and audio file type
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            filename = os.path.basename(path).replace(".txt", "")
            output_path = f"{output_folder}/{filename}.wav"

            # The response's audio_content is binary.
            with open(output_path, "wb") as f:
                # Write the response to the output file.
                f.write(response.audio_content)
                print(f'Audio content written to {output_path}')
        except:
            print(f"Failed for file: {path}")