@echo off
title Wishlist Tracker
color 0A

cd /d "%~dp0"
call .venv\Scripts\activate

python run.py

pause