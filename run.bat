@echo off
chcp 65001 > nul
title Golike Auto Job - Claim Bot
cd /d "%~dp0"
python golike_bot.py
pause
