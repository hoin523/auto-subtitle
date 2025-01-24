@echo off
:: Python Scripts 디렉토리 경로를 얻어 변수에 저장
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.exec_prefix + "\\Scripts")"') do set PYTHON_SCRIPTS=%%i

:: Python Scripts 경로를 PATH 환경 변수에 추가
setx PATH "%PATH%;%PYTHON_SCRIPTS%"

:: pip install . 명령어를 해당 디렉토리에서 실행
cd /d %PYTHON_SCRIPTS%
echo Installing using pip...
pip install .

:: 필수 라이브러리 설치
echo Installing required libraries...
pip install tqdm ffmpeg-python whisper

:: GitHub에서 auto-subtitle 패키지 설치 (필요 시 활성화)
@REM echo Installing auto-subtitle from GitHub...
@REM pip install git+https://github.com/hoin523/auto-subtitle.git

:: 설치 완료 메시지 출력
echo Installation completed successfully!
echo Required libraries (tqdm, ffmpeg-python, whisper) have been installed.
echo You can now use the auto-subtitle tool.

pause
