"""
Uploads and converts a PPTX to Google Slides using Google Drive API.

Place your OAuth client credentials file at `scripts/credentials.json` (create in Google Cloud Console, OAuth Desktop App).
First run will open a browser to authorize and create `scripts/token.json`.

Usage:
    python scripts/upload_to_google_slides.py --ppt results/presentation.pptx

Produces: a Google Slides URL printed to stdout.
"""
import os
import argparse
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']


def authorize(creds_path, token_path):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds


def upload_and_convert(pptx_path, creds):
    drive = build('drive', 'v3', credentials=creds)
    file_name = os.path.basename(pptx_path)
    media = MediaFileUpload(pptx_path, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')
    file_metadata = {'name': file_name, 'mimeType': 'application/vnd.google-apps.presentation'}
    uploaded = drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = uploaded.get('id')
    url = f'https://docs.google.com/presentation/d/{file_id}/edit'
    return file_id, url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ppt', default=os.path.join('results', 'presentation.pptx'), help='Path to PPTX')
    parser.add_argument('--credentials', default=os.path.join('scripts', 'credentials.json'), help='OAuth client credentials JSON')
    parser.add_argument('--token', default=os.path.join('scripts', 'token.json'), help='Path to store user token')
    args = parser.parse_args()

    if not os.path.exists(args.ppt):
        raise SystemExit(f'PPTX not found: {args.ppt}')
    if not os.path.exists(args.credentials):
        raise SystemExit(f'Credentials file not found: {args.credentials}\nCreate OAuth client credentials in Google Cloud Console (Application type: Desktop) and save as this path.')

    creds = authorize(args.credentials, args.token)
    file_id, url = upload_and_convert(args.ppt, creds)
    print('Uploaded and converted to Google Slides:')
    print(url)


if __name__ == '__main__':
    main()
