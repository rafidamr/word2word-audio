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
        print(translation)
        print(f"Translated text: {translation.translated_text}")
        print("-" * 100)

    return response


translate_text(
    texts=["إِنَّ أَحْسَنَ الْحَدِيثِ كِتَابُ اللَّهَ", "مِنْ شِرِّ الوَسْواسِ الخَنّاس"],
    source_lang="ar",
    target_lang="en"
)
