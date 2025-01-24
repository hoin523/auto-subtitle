from setuptools import setup, find_packages

setup(
    name="auto_subtitle",  # 패키지 이름
    version="1.0",
    packages=find_packages(),  # auto_subtitle 패키지를 찾음
    install_requires=[
        "openai-whisper",  # 자막 생성을 위한 Whisper 모델
        "ffmpeg-python",    # 비디오 처리 위한 FFmpeg
    ],
    entry_points={
        'console_scripts': ['auto_subtitle=auto_subtitle.cli:main'],
    },
    description="Automatically generate and embed subtitles into your videos",
)
