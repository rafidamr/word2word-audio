import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Set the path to the JSON key file for your service account
SERVICE_ACCOUNT_FILE = '/home/rafid_tijarah/credentials/auspicious-env-431402-q5-03a9c693508b.json'

# Define the scopes (Google Drive)
SCOPES = ['https://www.googleapis.com/auth/drive']

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Google Drive service
drive_service = build('drive', 'v3', credentials=credentials)

# File to upload
all_paths = [
    # 1
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/assets/weights/1--220.pth',
        '1eaUhwJxLb_VoOdUuDFqR_k3d8-uZncvi'
    ),
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/logs/1--220/added_IVF4119_Flat_nprobe_1_1--220_v2.index',
        '1eaUhwJxLb_VoOdUuDFqR_k3d8-uZncvi'
    ),
    # 2
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/assets/weights/2--3__.pth',
        '1K-YZCtFXzTIKU-g3ndFCWPrXqKJaZUUK'
    ),
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/logs/2--3__/added_IVF2251_Flat_nprobe_1_2--3___v2.index',
        '1K-YZCtFXzTIKU-g3ndFCWPrXqKJaZUUK'
    ),
    # 3
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/assets/weights/ar-splitted-speaker-A-train6.pth',
        '1FmOAfiZgjUwXdwgd_G-XErhYWw5IEzlp'
    ),
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/logs/ar-splitted-speaker-A-train6/added_IVF1151_Flat_nprobe_1_ar-splitted-speaker-A-train6_v2.index',
        '1FmOAfiZgjUwXdwgd_G-XErhYWw5IEzlp'
    ),
    # 4
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/assets/weights/4--_6_.pth',
        '1LmGGe04sErzGcgDytoJjhV4C1BnmgTk8'
    ),
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/logs/4--_6_/added_IVF1547_Flat_nprobe_1_4--_6__v2.index',
        '1LmGGe04sErzGcgDytoJjhV4C1BnmgTk8'
    ),
    # 5
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/assets/weights/5--_4_.pth',
        '1qEXcEni4jbEUZq6lIxiZcH4z43thxo4J'
    ),
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/logs/5--_4_/added_IVF3423_Flat_nprobe_1_5--_4__v2.index',
        '1qEXcEni4jbEUZq6lIxiZcH4z43thxo4J'
    ),
    # 6
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/assets/weights/6--__8.pth',
        '1lmSpTmy96Ibq9NJxzUW0JRyCWbVJw7l0'
    ),
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/logs/6--__8/added_IVF3069_Flat_nprobe_1_6--__8_v2.index',
        '1lmSpTmy96Ibq9NJxzUW0JRyCWbVJw7l0'
    ),
    # 7
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/assets/weights/7--_32.pth',
        '1rH3NGPpldoM5LZ5kpzb3N5--7UfFgyz6'
    ),
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/logs/7--_32/added_IVF1565_Flat_nprobe_1_7--_32_v2.index',
        '1rH3NGPpldoM5LZ5kpzb3N5--7UfFgyz6'
    ),
    # 8
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/assets/weights/8--8_3.pth',
        '1itM9LwT4p3OFRwWbGli9HFEVpjRTrYJS'
    ),
    (
        '/home/rafid_tijarah/rvc-trainer/Retrieval-based-Voice-Conversion-WebUI/logs/8--8_3/added_IVF1387_Flat_nprobe_1_8--8_3_v2.index',
        '1itM9LwT4p3OFRwWbGli9HFEVpjRTrYJS'
    )
]

for file_path, folder_id in all_paths:
    file_name = os.path.basename(file_path)

    # Define file metadata
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]  # Upload to a specific folder
    }

    # Upload the file
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f'File ID: {uploaded_file.get("id")} uploaded successfully to Google Drive.')