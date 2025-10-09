@echo off
chcp 65001 >nul
echo ========================================
echo ValueScan 启动器
echo ========================================
echo.

python start_with_chrome.py

if errorlevel 1 (
    echo.
    echo 程序异常退出
    pause
)
