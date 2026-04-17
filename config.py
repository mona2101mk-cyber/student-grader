# config.py

# Accuracy thresholds
ACCURACY_THRESHOLD_MIN = 30
ACCURACY_THRESHOLD_MAX = 100

# LLM Settings
LLM_MODEL = "mistral"  # or "llama2"
LLM_TEMPERATURE = 0.3
LLM_TIMEOUT = 60

# OCR Settings
OCR_CONFIDENCE_THRESHOLD = 0.3
USE_PADDLEOCR = True  # Set False to use Tesseract

# PDF Settings
DEFAULT_PAGES_TO_ANALYZE = 10