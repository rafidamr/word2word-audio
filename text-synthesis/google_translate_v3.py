# Imports the Google Cloud Translation library
import os

from google.cloud import translate_v3

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")


# Initialize Translation client
def translate_text(
    texts: list = [],
    source_lang: str  = None,
    target_lang: str = None,
) -> translate_v3.TranslationServiceClient:
    # Available languages: https://cloud.google.com/translate/docs/languages#neural_machine_translation_model

    client = translate_v3.TranslationServiceClient()
    parent = f"projects/{PROJECT_ID}/locations/global"

    # Supported mime types: # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        contents=texts,
        source_language_code=source_lang,
        target_language_code=target_lang,
        parent=parent,
        mime_type="text/plain",
    )

    # Display the translation for each input text provided
    for translation in response.translations:
        print(f"Translated text: {translation.translated_text}")
        print("-" * 100)

    return response

BATCH_SIZE = 50
speakers = ["1", "2", "3", "4", "5", "6", "7", "8"]
# BATCH_SIZE = 3
# speakers = ["0"]
SOURCE_LANG = "ar"
TARGET_LANG = "id"
PART = "2"

for speaker_id in speakers:
    transcript_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{speaker_id}/transcript"
    # transcript_folder = f"/home/rafid_tijarah/downloads/audio-inference/{speaker_id}/translation/ar-to-en"
    transcripts = [os.path.join(transcript_folder, f) for f in os.listdir(transcript_folder) if f.startswith(f'{PART}_')]

    texts = []
    for t in transcripts:
        with open(t, mode='r') as f:
            content = f.read()
            if content:
                texts.append(content)
            else:
                texts.append(',')

    translations = []
    if texts:
        for lower_bound in range(0, len(texts), BATCH_SIZE):
            print(f"speaker_id={speaker_id}")
            response = translate_text(
                texts=texts[lower_bound:lower_bound+BATCH_SIZE],
                source_lang=SOURCE_LANG,
                target_lang=TARGET_LANG
            )
            translations.extend(response.translations)

    if translations:
        output_folder = f"/home/rafid_tijarah/inference-results-gcp-stt/{speaker_id}/translation/{SOURCE_LANG}-to-{TARGET_LANG}"
        os.makedirs(output_folder, exist_ok=True)

        for i, translation in enumerate(translations):
            filename = os.path.basename(transcripts[i]).replace(".txt", "")
            translation_filename = os.path.join(output_folder, f"{filename}.txt")

            with open(translation_filename, mode='w') as f:
                f.write(translation.translated_text)