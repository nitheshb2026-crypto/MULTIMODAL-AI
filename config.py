import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "multimodal_health.db")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Medical safety disclaimer constant
MEDICAL_SAFETY_DISCLAIMER = (
    "⚠️ CLINICAL AI ASSISTANT NOTICE: This system provides algorithmic summaries and educational explanations "
    "based on uploaded biosignals, images, and tabular laboratory metrics. It is designed solely as a clinical decision support prototype "
    "and does not constitute definitive medical advice or diagnosis. Always consult certified healthcare providers."
)
