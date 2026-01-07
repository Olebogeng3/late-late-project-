Presentation generated from results/evaluation_metrics.json and images in this folder.

Files produced:
- presentation.pptx : Slide deck with Table of Contents, Metrics slide, Visual slides, and Conclusions.

To upload to Google Slides:
1. Open Google Drive and click New → File upload.
2. Upload `presentation.pptx` from the `results` folder.
3. Once uploaded, right-click the file → Open with → Google Slides. Google will convert the PPTX to Slides format.

If you want me to push a Slides file directly via the Google Drive API (converts PPTX to Slides), follow these steps.

Automated upload (recommended for many files)
1. Create OAuth Desktop credentials in Google Cloud Console and download the JSON as `scripts/credentials.json`.
2. Install dependencies in your project venv:

```bash
pip install -r scripts/requirements_google_api.txt
```

3. Run the uploader (first run opens a browser to authorize):

```bash
python scripts/upload_to_google_slides.py --ppt results/presentation.pptx
```

4. After successful upload you'll get a Slides URL printed.

Notes: The uploader stores a short-lived user token at `scripts/token.json`. Keep your `credentials.json` private. If you want, I can run the upload for you if you provide credentials or run the authorization locally and paste the created `token.json` (not recommended to paste secrets here).
