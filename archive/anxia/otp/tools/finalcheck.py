"""Checks on the delivered file: loudness and true peak (ffmpeg ebur128), black frames (blackdetect), duration,
and speech-to-text of the final mix against the script (faster-whisper small, by character, homophones tolerated).
run with the library venv: $LIB/.venv/bin/python tools/finalcheck.py out/<film>.mp4"""
import sys, os, re, json, subprocess, difflib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
f = sys.argv[1]
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', f, '-filter_complex', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]; TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1]; LRA = re.findall(r'LRA:\s+([\d.]+) LU', r)[-1]
print(f'loudness {I} LUFS, true peak {TP} dBTP, LRA {LRA} LU')
b = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', f, '-vf', 'blackdetect=d=0.1:pix_th=0.04', '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr
blacks = re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', b)
print('black frames:', blacks or 'none')
d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_name,pix_fmt,width,height,r_frame_rate', '-of', 'json', f], capture_output=True, text=True).stdout
print('streams:', json.dumps(json.loads(d), ensure_ascii=False))
wav = os.path.join(ROOT, 'review', 'finalcheck.wav')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f, '-ac', '1', '-ar', '16000', wav], check=True)
from faster_whisper import WhisperModel
m = WhisperModel('small', compute_type='int8')
segs, _ = m.transcribe(wav, language='zh', beam_size=5, initial_prompt='以下是普通话的句子。')
got = ''.join(s.text for s in segs)
want = ''.join(''.join(l['sub']) for l in json.load(open(os.path.join(ROOT, 'voice', 'lines.json'))) )   # the subtitles: numbers as digits, as Whisper writes them
norm = lambda s: re.sub(r'[\s，。：；？、！「」,.:;?!\-]', '', s)
sim = difflib.SequenceMatcher(None, norm(want), norm(got)).ratio()
print('heard:', got)
print(f'speech vs script similarity {sim:.3f}')
