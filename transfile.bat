@echo off
:: 코드 페이지를 UTF-8로 변경
chcp 65001

:: 시작 시간 측정
for /f "tokens=1-4 delims=:." %%a in ("%time%") do (
    set /a start_hour=%%a
    set /a start_minute=%%b
    set /a start_second=%%c
    set /a start_millisecond=%%d
)

:: 파일 경로를 입력받기
set /p file_path="파일 경로를 입력해주세요: "

:: 파일 경로가 유효한지 체크
if not exist "%file_path%" (
    echo 입력한 파일 경로가 존재하지 않습니다. 다시 시도해주세요.
    pause
    exit /b
)

:: 사용자로부터 변환할 언어 선택 받기
set /p lang="어떤 언어로 변경하시겠습니까? ex) ko, en, es: "

:: 언어 선택이 유효한지 확인
if not "%lang%"=="ko" if not "%lang%"=="en" if not "%lang%"=="es" if not "%lang%"=="fr" if not "%lang%"=="de" (
    echo 지원되지 않는 언어입니다. ko, en, es, fr, de 중에서 선택해주세요.
    pause
    exit /b
)

:: 현재 배치 파일의 경로 저장
set current_dir=%cd%

:: 입력된 파일명 추출 (확장자 제외)
for %%f in ("%file_path%") do set file_name=%%~nf

:: 출력 디렉토리 생성 (기존 파일명 폴더)
set output_dir=%current_dir%\%file_name%
mkdir "%output_dir%"

:: 선택한 언어와 파일을 사용하여 자막 변환 실행
echo 변환 중...
auto_subtitle "%file_path%" --output_dir "%output_dir%" --output_srt True --language %lang%

:: Python 명령어 실행 후 오류 체크
if %errorlevel% neq 0 (
    echo 오류 발생: 명령어 실행 중 문제가 발생했습니다. 확인 후 다시 시도해주세요.
    pause
    exit /b
)

:: 변환된 srt 파일 경로 확인
echo 변환된 자막 파일이 "%output_dir%"에 생성되었습니다.

:: 자막을 비디오에 추가하여 새로운 MP4 파일 생성
:: echo 자막을 비디오에 추가 중...
:: ffmpeg -i "%file_path%" -vf "subtitles='%output_dir%\\%file_name%.srt'" -c:a copy -c:v libx264 -crf 23 "%output_dir%\\%file_name%_with_subtitles.mp4"

:: ffmpeg 실행 후 오류 체크
if %errorlevel% neq 0 (
    echo 오류 발생: 비디오에 자막을 추가하는 중 문제가 발생했습니다.
    pause
    exit /b
)

:: 종료 시간 측정
for /f "tokens=1-4 delims=:." %%a in ("%time%") do (
    set /a end_hour=%%a
    set /a end_minute=%%b
    set /a end_second=%%c
    set /a end_millisecond=%%d
)

:: 시간 차이 계산 (시작 시간과 종료 시간의 차이를 계산)
set /a elapsed_hour=%end_hour% - %start_hour%
set /a elapsed_minute=%end_minute% - %start_minute%
set /a elapsed_second=%end_second% - %start_second%
set /a elapsed_millisecond=%end_millisecond% - %start_millisecond%

:: 시간이 음수일 경우 24시간을 더해주기
if %elapsed_second% lss 0 (
    set /a elapsed_second+=60
    set /a elapsed_minute-=1
)

if %elapsed_minute% lss 0 (
    set /a elapsed_minute+=60
    set /a elapsed_hour-=1
)

if %elapsed_hour% lss 0 (
    set /a elapsed_hour+=24
)

:: 변환 완료 메시지 출력 및 시간 출력
echo 변환이 완료되었습니다! 변환된 파일은 "%output_dir%"에 저장되었습니다.
echo 변환 시간: %elapsed_hour%시간 %elapsed_minute%분 %elapsed_second%초 %elapsed_millisecond%밀리초

:: 배치 파일 종료 전에 계속 열려있게 설정
pause
