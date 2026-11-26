#!/usr/bin/env python3
"""Build Coreboard offline English Piper recordings from the checked-in audio manifest.
Requires Piper voice ONNX and piper-tts. Never sends child data to the network.
"""
import argparse, hashlib, json, os, subprocess, tempfile, wave
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[1]
AUDIO=PROJECT/"audio"
def digest(path):
    d=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""): d.update(b)
    return d.hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--model",type=Path,required=True)
    parser.add_argument("--only",help="audio/manifest.json relative MP3, e.g. first/play-favourite.mp3")
    args=parser.parse_args()
    manifest=json.loads((AUDIO/"manifest.json").read_text(encoding="utf8"))
    if digest(args.model)!=manifest["voice_model_sha256"]:
        parser.error("voice model SHA256 does not match manifest")
    from piper import PiperVoice
    voice=PiperVoice.load(str(args.model))
    samples=manifest["audio"]
    keys=[args.only] if args.only else list(samples)
    if any(k not in samples for k in keys): parser.error("unknown --only path")
    for n,k in enumerate(keys,1):
        dest=(AUDIO/k).resolve()
        if not dest.is_relative_to(AUDIO.resolve()) or dest.suffix!=".mp3": raise RuntimeError("unsafe path "+k)
        dest.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="qixun-piper-") as t:
            wav=Path(t)/"voice.wav"
            mp3=Path(t)/"voice.mp3"
            with wave.open(str(wav),"wb") as o: voice.synthesize_wav(samples[k],o)
            normalized=Path(t)/"normalized.wav"
            subprocess.run(["ffmpeg","-hide_banner","-nostdin","-y","-v","error","-i",str(wav),"-af","loudnorm=I=-18:TP=-2:LRA=7","-ar","22050","-ac","1","-codec:a","pcm_s16le",str(normalized)],check=True)
            probe=subprocess.run(["ffmpeg","-hide_banner","-nostdin","-i",str(normalized),"-af","volumedetect","-f","null","-"],capture_output=True,text=True,check=True)
            import re
            match=re.search(r"mean_volume:\s*(-?[0-9.]+) dB",probe.stderr)
            if not match:raise RuntimeError("Cannot measure RMS level for "+k)
            adjust=-19.0-float(match.group(1))
            subprocess.run(["ffmpeg","-hide_banner","-nostdin","-y","-v","error","-i",str(normalized),"-af",f"volume={adjust:.2f}dB,alimiter=limit=0.89:level=false","-ar","22050","-ac","1","-codec:a","libmp3lame","-qscale:a","4",str(mp3)],check=True)
            if mp3.stat().st_size<100:raise RuntimeError("empty audio "+k)
            os.replace(mp3,dest)
        if n%10==0 or n==len(keys):print("built",n,"/",len(keys),flush=True)
    print("VOICE_BUILD_DONE",len(keys),flush=True)
if __name__=="__main__": main()
