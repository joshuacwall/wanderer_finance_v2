import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import base64
from dotenv import load_dotenv
import json

load_dotenv()

class GoogleDriveClient:
    def __init__(self):
        encoded_credentials = os.getenv("GOOGLE_CREDENTIALS")
        if not encoded_credentials:
            raise ValueError("GOOGLE_CREDENTIALS environment variable not set.")

        try:
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            creds_dict = json.loads(decoded_credentials)
            scopes = ['https://www.googleapis.com/auth/drive']  # Correct scope for Drive
            creds = service_account.Credentials.from_service_account_info(info=creds_dict, scopes=scopes)
            self.service = build('drive', 'v3', credentials=creds) # Build Drive service
        except Exception as e:
            raise ValueError(f"Error authenticating: {e}")

    def upload_or_overwrite_file(self, file_path, drive_folder_id, mime_type=None):
        """Uploads a file to Google Drive, overwriting if it exists."""

        file_name = os.path.basename(file_path)

        try:
            # 1. Check if the file already exists in the specified folder
            query = f"name='{file_name}' and '{drive_folder_id}' in parents and trashed = false"
            results = self.service.files().list(q=query, spaces='drive').execute()
            files = results.get('files', [])

            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True) # Set mimetype if needed

            if files:  # File exists, update it
                file_id = files[0].get('id')
                updated_file = self.service.files().update(fileId=file_id, media_body=media).execute()
                print(f"File '{file_name}' updated in Google Drive.")
                return updated_file

            else:  # File doesn't exist, create it
                file_metadata = {'name': file_name, 'parents': [drive_folder_id]} # Add the folder
                new_file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f"File '{file_name}' uploaded to Google Drive.")
                return new_file

        except Exception as e:
            print(f"An error occurred during file upload/update: {e}")
            return None