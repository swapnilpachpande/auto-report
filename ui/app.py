
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
st.title("📜 File Upload (Input)")

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
    pdf_path = Path(output_path)

#============pdf_report_download==============

st.title("📄 PDF report (Output)")

#placeholder for pdf report download - later this will call into pdf_report.py

# if st.button("Generate PDF Report"):
#     # TODO: Integrate with pdf_report.py
#     # from pdf_report import generate_pdf_report
#     # pdf_path = create_report(data=your_data)
#     st.warning("PDF report generation not yet implemented.")

#where we expect pdf file to appear
#adjust to match whatever pdf_report.py uses

if uploaded_file is not None:
    if pdf_path.exists():
        with pdf_path.open("rb") as f:
            st.download_button(
                label="Download PDF Report",
                data=f,
                file_name="AI_Data_Report.pdf",
                mime="application/pdf",
                key="download-pdf",
            )
    else:
        st.info("PDF report not found. Once the backend creates a pdf you will see a download button here.")

#display the report on UI


if uploaded_file is not None:
    if report_text is not None:
        st.title("📝 Report Text Output")
        st.text(report_text)