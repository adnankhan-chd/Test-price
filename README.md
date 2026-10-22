# Car Identifier (Streamlit + Gemini Flash)

A small Streamlit app that accepts a car photo and asks Google's Gemini Flash model to estimate the vehicle's make, model, likely year range, and approximate price range for a chosen market.

> **Important:** This is an AI-generated estimate, not a verified vehicle valuation or live-market quote. A photo usually cannot establish mileage, accident history, exact trim, registration status, or mechanical condition. Verify the result against current local listings.

## Features

- Upload JPG, PNG, or WebP car photos (maximum 10 MB)
- Identify likely brand, model, year range, and trim
- Choose market/country, currency, and assumed condition
- Display an approximate price range and uncertainty notes
- Keep the Gemini API key out of source code

## Requirements

- Python 3.10 or newer
- A Google Gemini API key with access to the configured model

## Run locally

1. Download or clone this project and open a terminal in the project folder.
2. Create and activate a virtual environment:

   **macOS/Linux**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` and add your key:

   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   ```

   Create the `.streamlit` folder first if it doesn't exist. Alternatively, set an environment variable named `GEMINI_API_KEY`.

5. Start the app:

   ```bash
   streamlit run app.py
   ```

## Push to GitHub

1. Create a new, empty repository on GitHub.
2. Make sure secrets and local environment files are ignored. Create a `.gitignore` file containing:

   ```gitignore
   .venv/
   __pycache__/
   .streamlit/secrets.toml
   .env
   *.py[cod]
   ```

3. From the project folder, run (replace the URL with your own repository URL):

   ```bash
   git init
   git add app.py README.md requirements.txt .gitignore
   git commit -m "Initial car identifier app"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   git push -u origin main
   ```

   If Git reports that `origin` already exists, use `git remote set-url origin YOUR_REPOSITORY_URL`.

**Never commit your API key.** If you accidentally publish it, revoke it and create a new key.

## Deploy on Streamlit Community Cloud

1. Push the code to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in.
3. Choose **Create app**, then select your repository, branch (`main`), and main file path (`app.py`).
4. In the app's **Advanced settings / Secrets** area, add this TOML secret:

   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   ```

5. Deploy the app. Streamlit installs the packages from `requirements.txt`.
6. Open the app URL and test it with a clear car image.

If deployment fails, inspect the app logs. Confirm that the repository includes `app.py` and `requirements.txt`, the secret is spelled exactly `GEMINI_API_KEY`, and your key has Gemini API access and quota.

## Notes and limitations

- The configured model is `gemini-flash-latest`, Google's moving alias for a current Flash model. If that alias is unavailable for your API account, replace `MODEL_NAME` in `app.py` with a supported Flash model name from the Gemini API documentation.
- The app asks Gemini to estimate prices from its learned knowledge; it does **not** query live classified ads or dealer inventory.
- Price ranges vary by market, date, trim, mileage, condition, import taxes, and currency. Consider integrating a trusted local listings/pricing API if reliable market pricing is a core product feature.
- Uploaded images are sent to the Gemini API for analysis. Tell users this in your privacy notice before launching publicly.
