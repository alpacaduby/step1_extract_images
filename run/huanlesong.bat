@echo off
:: 第一步：强制设置控制台编码为UTF-8（必须放在最开头）
chcp 65001 >nul 2>&1
:: 设置窗口标题
title 批量提取视频帧工具
:: 关闭命令回显（避免冗余输出）
setlocal enabledelayedexpansion

:: ====================== 配置区域（请严格按实际路径修改）======================
:: 1. Python路径：如果输入python -V提示找不到，改为完整路径（如C:\Python310\python.exe）
set "PYTHON_PATH=python"
:: 2. 你的Python脚本路径（优先用绝对路径，避免相对路径出错）
:: 示例：绝对路径（推荐）：set "SCRIPT_NAME=F:\项目\vlm_eval\step1_extract_images\v1_args.py"
:: 示例：相对路径（需bat和vlm_eval目录在同一级）：set "SCRIPT_NAME=vlm_eval\step1_extract_images\v1_args.py"
set "SCRIPT_NAME=vlm_eval\step1_extract_images\v1_args.py"
:: 3. 视频输入目录（必须是绝对路径，避免相对路径歧义）
set "INPUT_DIR=F:\欢乐颂"
:: 4. 输出基础目录（支持相对/绝对路径）
set "OUTPUT_BASE_DIR=vlm_eval\step1_extract_images\images"
:: 5. 提取间隔（秒）
set "INTERVAL_SECONDS=10"
:: ===========================================================================

:: ====================== 关键检查：避免执行后报错 ======================
:: 检查Python脚本是否存在
if not exist "%SCRIPT_NAME%" (
    echo 【错误】未找到Python脚本文件：%SCRIPT_NAME%
    echo 请检查SCRIPT_NAME配置是否正确！
    pause
    exit /b 1
)

:: 检查输入目录是否存在
if not exist "%INPUT_DIR%" (
    echo 【错误】输入目录不存在：%INPUT_DIR%
    echo 请检查INPUT_DIR配置是否正确！
    pause
    exit /b 1
)

:: ====================== 打印配置信息 ======================
echo ====================== 配置信息 ======================
echo Python路径：%PYTHON_PATH%
echo 脚本路径：%SCRIPT_NAME%
echo 输入目录：%INPUT_DIR%
echo 输出目录：%OUTPUT_BASE_DIR%
echo 提取间隔：%INTERVAL_SECONDS%秒
echo ======================================================
echo.
echo 开始执行脚本...
echo.

:: ====================== 执行Python脚本 ======================
:: 路径用双引号包裹，避免空格/中文引发语法错误
"%PYTHON_PATH%" "%SCRIPT_NAME%" -i "%INPUT_DIR%" -o "%OUTPUT_BASE_DIR%" -s %INTERVAL_SECONDS%

:: ====================== 执行结果提示 ======================
echo.
echo ====================== 执行结束 ======================
if %errorlevel% equ 0 (
    echo 脚本执行成功！
) else (
    echo 脚本执行出错（错误码：%errorlevel%），请检查以上报错信息！
)
pause
endlocal