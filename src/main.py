import os
import sys
from pathlib import Path
import pandas as pd

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from src.ai_summary import AiSummary
from src.data_ingestion import DataIngestion
import json
        
def generate_report(df_oai: pd.DataFrame = None):
    """
    Generate a report from a pandas DataFrame or (if df_oai is None) from the default WHR_2015.csv file.

    This function is callable from other modules (for example, `app.py` can pass the
    uploaded DataFrame as `df_oai`). When called as a script, it will read the built-in
    `data/WHR_2015.csv` file.

    Returns a tuple: (report_text: str, output_file: Path)
    """
    project_root = Path(__file__).resolve().parents[1]


    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. Please set it in your environment or create a .env file"
        )

    # Get model name from environment or use default
    model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    try:
        # Require a DataFrame from callers (don't read default CSV automatically)
        if df_oai is None:
            raise ValueError(
                "df_oai was not provided. When calling generate_report programmatically, pass a pandas DataFrame."
            )
        df = df_oai

        print("\n🤖 Generating comprehensive report...")
        # get basic summary
        basic_stats, numeric_stats, categorical_stats, datetime_stats = DataIngestion.generate_basic_stats(df)
        basic_summary = {
            "basic_stats": basic_stats,
            "numeric_stats": numeric_stats,
            "categorical_stats": categorical_stats,
            "datetime_stats": datetime_stats,
        }
        # Build a combined report text: pretty-print basic summary then AI interpretation
        try:
            basic_text = json.dumps(basic_summary, indent=2, default=str)
        except Exception:
            basic_text = str(basic_summary)

        # Initialize the AI Summary generator
        summary_generator = AiSummary.get_ai_model(
            api_key=api_key,
            model_name=model_name,
        )

        ai_summary = summary_generator.generate_ai_summary(basic_text)
        print('-----------------------ai_summary--------------------')
        print(ai_summary)
        print('-----------------------------------------------------')

        
        # Generate EDA visualizations
        from src.eda_visualization import generate_visualizations
        visualization_paths = generate_visualizations(df)

        # Generate PDF report with visualizations
        from src.pdf_report import generate_pdf_report
        report_path = project_root / "reports"
        
        pdf_file = generate_pdf_report(
            report_path=report_path,
            basic_stats=basic_summary,
            ai_summary=ai_summary,
            visualization_paths=visualization_paths
        )

        # Save the report with timestamp (text version for reference)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path.mkdir(exist_ok=True)
        output_file = report_path / f"whr_2015_analysis_{timestamp}.txt"


        ai_text = ai_summary if isinstance(ai_summary, str) else str(ai_summary)

        report_text = "".join([
            "=== BASIC STATISTICS ===\n",
            basic_text,
            "\n\n=== AI-INTERPRETATION ===\n",
            ai_text,
        ])

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_text)

        # Print the report to console as well
        print("\n📝 Report Contents:")
        print("=" * 80)
        #print(report_text)
        print("=" * 80)

        print(f"\n Text report saved to: {output_file}")
        print(f" PDF report generated: {pdf_file}")
        return str(pdf_file), report_text

    except Exception as e:
        print(f"\n Error generating report: {str(e)}")
        raise

if __name__ == "__main__":
    # Keep CLI behavior: when run as a script, generate report from default CSV
    generate_report()
