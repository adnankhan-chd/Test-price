import json
import os
import re

import streamlit as st
from google import genai
from google.genai import types

MODEL_NAME = "gemini-flash-latest"
MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

st.set_page_config(page_title="Car Identifier", page_icon="🚘", layout="centered")

st.title("🚘 Car Identifier")
st.write(
    "Upload a car photo to identify its likely make, model, year range, and an "
    "approximate market price."
)
st.caption(
    "AI identification and pricing are estimates, not a professional appraisal. "
    "A photo alone may not reveal the exact trim, condition, mileage, or history."
)

with st.sidebar:
    st.header("Estimate settings")
    country = st.text_input("Country / market", value="Pakistan")
    currency = st.text_input("Currency", value="PKR")
    condition = st.selectbox(
        "Assumed condition",
        ["Used — average condition", "Used — good condition", "New"],
    )
    st.caption("Price estimates depend heavily on market, trim, mileage, and condition.")

def get_api_key():
    """Read the key from Streamlit secrets first, then environment variables."""
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = ""
    return secret_key or os.getenv("GEMINI_API_KEY", "")

def extract_json(text):
    """Parse JSON, tolerating a fenced JSON response if the model adds one."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("The AI response did not contain a JSON object.")
    return json.loads(cleaned[start:end + 1])

def identify_car(image_bytes, mime_type, api_key, market, currency_code, assumed_condition):
    client = genai.Client(api_key=api_key)
    prompt = f"""
Analyze the uploaded image and identify the main passenger vehicle if one is visible.
Return ONLY one valid JSON object with these keys:
{{
  "is_car": true,
  "brand": "manufacturer / make",
  "model": "model name",
  "year_range": "likely year range or Unknown",
  "variant_or_trim": "likely trim or Unknown",
  "confidence": "High, Medium, or Low",
  "price_min": 0,
  "price_max": 0,
  "currency": "{currency_code}",
  "market": "{market}",
  "price_basis": "one short explanation",
  "notes": ["short uncertainty or identification notes"]
}}
Rules:
- If no car is clearly visible, set is_car to false, brand/model/year_range/variant_or_trim
  to "Unknown", price_min and price_max to 0, and explain in notes.
- Do not claim certainty when badges, body details, or the image are unclear.
- Estimate a plausible current asking-price range for the specified market, in {currency_code},
  for this assumed condition: {assumed_condition}.
- Use numeric values for price_min and price_max (no commas or currency symbols).
- If you cannot responsibly estimate a price, use 0 for both price values and explain why.
- Price is a rough AI estimate, not a live listing lookup. Do not imply you checked live listings.
- Keep notes concise. Return JSON only.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    return extract_json(response.text or "")

uploaded = st.file_uploader(
    "Upload a car photo",
    type=["jpg", "jpeg", "png", "webp"],
    help="JPG, PNG, or WebP; maximum 10 MB.",
)

if uploaded:
    image_bytes = uploaded.getvalue()
    mime_type = uploaded.type or "application/octet-stream"

    if mime_type not in ALLOWED_TYPES:
        st.error("Please upload a JPG, PNG, or WebP image.")
        st.stop()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        st.error("The image is larger than 10 MB. Please upload a smaller image.")
        st.stop()

    st.image(image_bytes, caption="Uploaded photo", use_container_width=True)

    if st.button("Identify car and estimate price", type="primary", use_container_width=True):
        api_key = get_api_key()
        if not api_key:
            st.error(
                "Gemini API key not found. Add GEMINI_API_KEY to your local "
                ".streamlit/secrets.toml file or to your deployment secrets."
            )
            st.stop()

        with st.spinner("Analyzing the photo…"):
            try:
                result = identify_car(
                    image_bytes, mime_type, api_key, country, currency, condition
                )
            except Exception as exc:
                st.error(
                    "Could not analyze this image. Check your API key, internet "
                    "connection, Gemini API access, and model availability."
                )
                st.caption(f"Technical detail: {type(exc).__name__}: {exc}")
                st.stop()

        if not isinstance(result, dict):
            st.error("The AI returned an unexpected response. Please try again.")
            st.stop()

        if not result.get("is_car", False):
            st.warning("I couldn't confidently identify a car in this image.")
            notes = result.get("notes", [])
            if notes:
                st.write(" ".join(map(str, notes)) if isinstance(notes, list) else str(notes))
            st.stop()

        st.subheader("Identification")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Brand", str(result.get("brand", "Unknown")))
            st.metric("Model", str(result.get("model", "Unknown")))
        with col2:
            st.metric("Likely year", str(result.get("year_range", "Unknown")))
            st.metric("Confidence", str(result.get("confidence", "Unknown")))

        st.write("**Variant / trim:**", result.get("variant_or_trim", "Unknown"))

        low = result.get("price_min", 0)
        high = result.get("price_max", 0)
        price_currency = str(result.get("currency", currency)).strip()
        if isinstance(low, (int, float)) and isinstance(high, (int, float)) and low > 0 and high > 0:
            st.subheader("Estimated price range")
            st.markdown(f"### {price_currency} {low:,.0f} – {high:,.0f}")
        else:
            st.info("The model could not provide a reliable price range for this photo.")

        if result.get("price_basis"):
            st.write("**Pricing note:**", result["price_basis"])

        notes = result.get("notes", [])
        if notes:
            st.write("**Notes and uncertainties**")
            if isinstance(notes, list):
                for note in notes:
                    st.write(f"- {note}")
            else:
                st.write(str(notes))

        st.caption(
            "Verify the exact variant and compare current local listings before making "
            "a buying or selling decision. The estimate may be inaccurate."
        )
else:
    st.info("Upload a clear photo showing the car's front or rear, if possible.")
