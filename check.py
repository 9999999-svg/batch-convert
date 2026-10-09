SCRIPT = 'batch_convert.py'
MEDIA = False
"""One actual-files check; supports Python source or the standalone EXE."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--exe', type=Path)
parser.add_argument('--ffmpeg', type=Path)
args = parser.parse_args()
program = [str(args.exe.resolve())] if args.exe else [sys.executable, str(root / SCRIPT)]
environment = dict(os.environ)
ffmpeg = None
if MEDIA:
    ffmpeg = str(args.ffmpeg) if args.ffmpeg else shutil.which('ffmpeg')
    if not ffmpeg:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    assert Path(ffmpeg).is_file(), 'Provide FFmpeg with --ffmpeg'
    environment['PATH'] = str(Path(ffmpeg).parent) + os.pathsep + environment.get('PATH', '')
def run(*arguments):
    result = subprocess.run(program + list(map(str, arguments)), capture_output=True, text=True, encoding='utf-8', errors='replace', env=environment, timeout=90)
    assert result.returncode == 0, (result.stdout, result.stderr)
    return result.stdout
def make_video(path):
    subprocess.run([ffmpeg, '-y', '-f', 'lavfi', '-i', 'testsrc=size=96x64:rate=10', '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=44100', '-t', '1', '-pix_fmt', 'yuv420p', str(path)], capture_output=True, check=True, timeout=30)
assert 'usage:' in run('--help').lower()
with tempfile.TemporaryDirectory(prefix='工具检查 中文 ') as folder:
    temporary = Path(folder)
    input_dir, output_dir = temporary / '输入', temporary / '输出'
    input_dir.mkdir()
    from PIL import Image
    Image.new('RGBA', (120, 80), (255, 0, 0, 0)).save(input_dir / '中文.png')
    run('-i', input_dir, '-o', output_dir, '-f', 'jpg')
    with Image.open(output_dir / '中文.jpg') as image:
        assert min(image.getpixel((0, 0))) > 245
print('PASS: batch-convert, actual files, Chinese paths and CLI help.')
