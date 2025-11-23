
import streamlit as st
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from src.main import generate_report

# ============ Header Logo =============
# Load logo relative to this file so it works regardless of the current working directory
logo_path = Path(__file__).resolve().parent / "unt-stacked-logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=250)
else:
    st.warning(f"Logo not found at: {logo_path}")


#============Uploader==============


st.title("File Upload Example")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv","xlsx"])

# Load environment variables from .env file
project_root = Path(__file__).resolve().parents[1]
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

if uploaded_file is not None:
    df_oai = pd.read_csv(uploaded_file)
    output_path, report_text = generate_report(df_oai)
    st.success(f"Report saved to: {output_path}")
    #display the report on UI
    st.text(report_text)