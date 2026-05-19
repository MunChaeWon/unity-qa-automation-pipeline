@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

cd /d D:\funity\Test1

python qa-tools\run_qa_pipeline.py

pause