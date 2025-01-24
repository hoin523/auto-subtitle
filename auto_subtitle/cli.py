import os
import ffmpeg
import whisper
import argparse
import warnings
import tempfile
from .utils import filename, str2bool, write_srt
import time


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("audio", nargs="+", type=str, help="Paths to audio files to transcribe (e.g., mp3, wav, mp4)")
    parser.add_argument("--model", default="small", choices=whisper.available_models(), help="Name of the Whisper model to use")
    parser.add_argument("--output_dir", "-o", type=str, default=".", help="Directory to save the outputs")
    parser.add_argument("--output_srt", type=str2bool, default=False, help="Whether to output the .srt file along with the audio files")
    parser.add_argument("--verbose", type=str2bool, default=False, help="Whether to print out the progress and debug messages")
    parser.add_argument("--task", type=str, default="transcribe", choices=["transcribe", "translate"], help="Speech recognition or translation task")
    parser.add_argument("--language", type=str, default="auto", choices=["auto", "ko", "en", "es", "fr", "de"], help="Origin language of the audio")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # 작업 시작 시간 기록
    start_time = time.time()

    # 모델 로드
    print("[1/3] Loading Whisper model...")
    model = whisper.load_model(args.model)

    # 오디오 추출 및 변환
    print("\n[2/3] Extracting audio from input files...")
    audios = get_audio(args.audio)

    # 자막 생성
    print("\n[3/3] Generating subtitles...")
    subtitles = get_subtitles(
        audios,
        args.output_srt,
        args.output_dir,
        lambda audio_path: model.transcribe(audio_path, language=args.language)
    )

    # 자막을 비디오에 추가
#     for path, srt_path in subtitles.items():
#         if path.endswith(".mp4"):
#             print(f"Adding subtitles to video: {filename(path)}")
#             add_subtitles_to_video(path, srt_path, args.output_dir)

    # 작업 완료 시간 기록
    end_time = time.time()
    elapsed_time = end_time - start_time

    print("\n작업이 완료되었습니다!")
    print(f"총 소요 시간: {elapsed_time:.2f}초")
    print(f"결과는 다음 디렉토리에 저장되었습니다: {os.path.abspath(args.output_dir)}")

    os.system("pause")  # Windows 환경에서 창 종료 방지


def get_audio(paths):
    temp_dir = tempfile.gettempdir()
    audio_paths = {}
    for path in paths:
        try:
            print(f"Processing file: {filename(path)}")
            output_path = os.path.join(temp_dir, f"{filename(path)}.wav")
            # FFmpeg 변환 실행
            ffmpeg.input(path).output(
                output_path, acodec="pcm_s16le", ac=1, ar="16k"
            ).run(quiet=False, overwrite_output=True)
            audio_paths[path] = output_path
        except ffmpeg.Error as e:
            print(f"[Error] Failed to extract audio from {filename(path)}: {e.stderr.decode('utf-8')}")
            continue
    return audio_paths


def get_subtitles(audio_paths, output_srt, output_dir, transcribe):
    subtitles_path = {}
    for path, audio_path in audio_paths.items():
        try:
            print(f"Generating subtitles for: {filename(path)}")
            srt_path = os.path.join(output_dir, f"{filename(path)}.srt") if output_srt else tempfile.mktemp(suffix=".srt")
            txt_path = os.path.join(output_dir, f"{filename(path)}.txt")  # 저장할 TXT 파일 경로
            warnings.filterwarnings("ignore")

            result = transcribe(audio_path)
            print(f"Transcription result: {result}")  # 결과 출력 (디버그 용)

            warnings.filterwarnings("default")

            # SRT 파일 저장
            with open(srt_path, "w", encoding="utf-8") as srt:
                write_srt(result["segments"], file=srt)

            # TXT 파일 저장 (타임스탬프와 자막 내용)
            with open(txt_path, "w", encoding="utf-8") as txt:
                for segment in result["segments"]:
                    start = segment["start"]
                    end = segment["end"]
                    text = segment["text"]
                    txt.write(f"[{format_timestamp(start)} --> {format_timestamp(end)}]\n{text}\n\n")

            subtitles_path[path] = srt_path
            print(f"TXT 파일 저장 완료: {txt_path}")

        except Exception as e:
            print(f"[Error] Failed to generate subtitles for {filename(path)}: {e}")
    return subtitles_path


def format_timestamp(seconds):
    """초를 HH:MM:SS,mmm 형식으로 변환"""
    milliseconds = int((seconds % 1) * 1000)
    time_str = time.strftime('%H:%M:%S', time.gmtime(int(seconds)))
    return f"{time_str},{milliseconds:03d}"


def add_subtitles_to_video(video_path, srt_path, output_dir):
    output_path = os.path.join(output_dir, f"{filename(video_path)}_with_subtitles.mp4")
    try:
        # 자막 파일 경로 이스케이프 처리
        escaped_srt_path = srt_path.replace("\\", "\\\\").replace(":", "\\:")
        # ffmpeg 명령 실행
        ffmpeg.input(video_path).output(
            output_path,
            vf=f"subtitles='{escaped_srt_path}'",  # 자막 경로
            c="copy",  # 비디오와 오디오 복사
            strict="experimental"
        ).run(capture_stdout=True, capture_stderr=True)
        print(f"자막이 추가된 비디오가 생성되었습니다: {output_path}")
    except ffmpeg.Error as e:
        print(f"[Error] 비디오에 자막을 추가하는 데 실패했습니다: {e.stderr.decode('utf-8')}")
