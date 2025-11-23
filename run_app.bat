@echo off
cd %~dp0
python -m streamlit run ui/app.py
pause
