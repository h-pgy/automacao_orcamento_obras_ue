from config import ORIGINAL_DATA_DIR, GENERATED_DATA_DIR, SHEET_NAME, ROWS_TO_SKIP

from .extract import Extract

load_sheet = Extract(folder=ORIGINAL_DATA_DIR, sheet_name=SHEET_NAME, skiprows=ROWS_TO_SKIP)
