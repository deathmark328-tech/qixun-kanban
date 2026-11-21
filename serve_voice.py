#!/usr/bin/env python3
"""启洵看板 · 静态服务 + 语音提问后端（本机 Whisper + DeepSeek + edge-tts）。

端点：
  GET  /               静态文件
  POST /api/ask        原始音频（webm/mp4/wav）→ {heard, reply, audio}
  GET  /audio/<name>   合成语音
"""
import http.server
import json
import os
import re
import socketserver
import subprocess
import tempfile
import time
import urllib.request

DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(DIR, ".audio")
os.makedirs(AUDIO_DIR, exist_ok=True)
PORT = 8123

WHISPER = os.path.expanduser("~/projects/whisper.cpp/build/bin/whisper-cli")
WMODEL = os.path.expanduser("~/projects/whisper.cpp/models/ggml-small.bin")
DEEPSEEK_KEY = ""
KNOW_PATH = os.path.join(DIR, "knowledge", "qixun-knowledge.json")
KNOW = []


def load_knowledge():
    global KNOW
    try:
        d = json.load(open(KNOW_PATH, encoding="utf-8"))
        KNOW = d.get("chunks", [])
    except Exception:
        KNOW = []


def _grams(s):
    s = re.sub(r"\s+", "", s.lower())
    return {s[i:i + 2] for i in range(max(1, len(s) - 1))}


def retrieve(query, k=3):
    """轻量检索：字二元重叠 + 标签命中。无需外部 embedding。"""
    if not KNOW or not query:
        return []
    qg = _grams(query)
    scored = []
    for c in KNOW:
        text = c.get("text", "")
        tg = _grams(text)
        overlap = len(qg & tg) / (len(qg) + 1)
        tag_hit = sum(1 for t in c.get("tags", []) if t and t in query)
        score = overlap + 0.35 * tag_hit
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    return [c for s, c in scored[:k] if s > 0.02]


def load_key():
    global DEEPSEEK_KEY
    for p in [os.path.expanduser("~/.hermes/.env")]:
        try:
            for line in open(p, encoding="utf-8", errors="ignore"):
                m = re.match(r'^DEEPSEEK_API_KEY=["\']?([^"\'\s]+)', line)
                if m:
                    DEEPSEEK_KEY = m.group(1)
                    return
        except OSError:
            pass


SYSTEM = (
    "你是启洵的五岁小朋友语音助手，名字叫小星。"
    "他五岁，刚确诊ADHD，正在准备上小学。"
    "规则："
    "1) 每次只说一到两句话，短、慢、具体，不用抽象词。"
    "2) 回答用普通话，语气温和活泼，像幼儿园老师。"
    "3) 不谈任何吓人的、暴力的、成人的内容；被问到就温和地说'这个我们长大再聊'。"
    "4) 多鼓励他做流程里的事（刷牙、穿衣、收玩具）。"
    "5) 不要长篇大论，不要列条目。"
)


def transcribe(wav_path: str) -> str:
    out_prefix = wav_path + ".txt"
    cmd = [WHISPER, "-m", WMODEL, "-f", wav_path, "-l", "zh", "-otxt",
           "-of", out_prefix, "-np", "-t", "8"]
    subprocess.run(cmd, capture_output=True, timeout=180)
    p = out_prefix + ".txt"
    if os.path.exists(p):
        txt = open(p, encoding="utf-8", errors="replace").read().strip()
        return re.sub(r"\[[^\]]*\]", "", txt).strip()
    return ""


def ask_llm(text: str) -> str:
    if not DEEPSEEK_KEY:
        return "我现在还不能说话，要大人先给我装好钥匙。"
    mem = retrieve(text, 3)
    sys_prompt = SYSTEM
    if mem:
        sys_prompt += "\n\n你记得这些关于启洵的事（自然带出来，不要逐条背）：\n" + \
            "\n".join("- " + m["text"] for m in mem)
    payload = {
        "model": "deepseek-flash",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": text},
        ],
        "max_tokens": 600,
        "temperature": 0.6,
    }
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + DEEPSEEK_KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
            return d["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return "我有点听不清，再说一次好吗？（%s）" % type(e).__name__


def tts(text: str) -> str:
    name = "reply-%d.mp3" % int(time.time() * 1000)
    path = os.path.join(AUDIO_DIR, name)
    cands = [
        [os.path.expanduser("~/.local/bin/edge-tts")],
        ["edge-tts"],
        ["/usr/bin/python3", "-m", "edge_tts"],
        [os.path.expanduser("~/.venv/bin/python3"), "-m", "edge_tts"],
    ]
    for base in cands:
        try:
            subprocess.run(base + ["--voice", "zh-CN-XiaoxiaoNeural", "--rate=-12%",
                                   "--text", text, "--write-media", path],
                           capture_output=True, timeout=90)
            if os.path.exists(path) and os.path.getsize(path) > 800:
                return name
        except Exception:
            continue
    return ""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Service-Worker-Allowed", "/")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):  # noqa: A002
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/hello"):
            import datetime
            h = datetime.datetime.now().hour
            if h < 11:
                greet, py = "早上好", "zǎo shang hǎo"
            elif h < 17:
                greet, py = "下午好", "xià wǔ hǎo"
            else:
                greet, py = "晚上好", "wǎn shang hǎo"
            hooks = [
                "今天要不要先穿校服？", "你的午餐盒准备好了吗？",
                "要不要先看看今天要做哪几件？", "Mrs Hamonds 今天会不会夸你？"
            ]
            import random
            return self._json({"greet": greet, "py": py,
                               "hook": random.choice(hooks),
                               "name": "启洵"})
        return super().do_GET()

    def do_POST(self):
        if not self.path.startswith("/api/ask"):
            return self._json({"error": "not found"}, 404)
        try:
            n = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(n)
            if len(raw) < 800:
                return self._json({"error": "录音太短"}, 400)

            with tempfile.TemporaryDirectory() as td:
                src = os.path.join(td, "in.bin")
                wav = os.path.join(td, "in.wav")
                open(src, "wb").write(raw)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src,
                                "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav],
                               capture_output=True, timeout=120)
                if not os.path.exists(wav):
                    return self._json({"error": "音频解析失败"}, 400)
                heard = transcribe(wav)

            if not heard:
                return self._json({"heard": "", "reply": "我没听清，再说一次好吗？", "audio": ""})

            reply = ask_llm(heard)
            audio = tts(reply)
            return self._json({"heard": heard, "reply": reply,
                               "audio": ("/audio/" + audio) if audio else ""})
        except Exception as e:
            return self._json({"error": "%s: %s" % (type(e).__name__, e)}, 500)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    load_key()
    load_knowledge()
    with Server(("0.0.0.0", PORT), Handler) as httpd:
        print("serving %s on 0.0.0.0:%d  (deepseek key: %s)"
              % (DIR, PORT, "yes" if DEEPSEEK_KEY else "MISSING"))
        httpd.serve_forever()
