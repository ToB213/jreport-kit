"""Local PDF preview using only the Python standard library."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import webbrowser

PAGE = """<!doctype html>
<html lang="ja"><meta charset="utf-8"><title>研究報告プレビュー</title>
<style>
body{margin:0;font:14px system-ui;background:#eee}
header{padding:8px 16px;display:flex;gap:16px;align-items:center}
iframe{display:block;width:100%;height:calc(100vh - 40px);border:0}
</style>
<header><span id="status">初回ビルドを待っています</span>
<a href="/report.pdf" target="_blank">PDFを開く</a></header>
<iframe title="研究報告PDF"></iframe>
<script>
let version = null;
async function poll() {
  try {
    const response = await fetch('/status', {cache:'no-store'});
    const state = await response.json();
    document.querySelector('#status').textContent = state.message;
    if (state.version && state.version !== version) {
      document.querySelector('iframe').src = '/report.pdf?v=' + state.version;
      version = state.version;
    }
  } catch (_) {
    document.querySelector('#status').textContent = '接続が切れました。起動したターミナルを確認してください';
  }
  setTimeout(poll, 1000);
}
poll();
</script></html>""".encode()


def preview(command, source, output, env, root, port):
    stop = threading.Event()
    lock = threading.Lock()
    state = {"message": "初回ビルドを待っています", "version": None}
    pdf = None

    def fingerprint():
        paths = [root / '.latexmkrc']
        for folder in (source.parent, root / 'bib', root / 'sty'):
            paths.extend(p for p in folder.rglob('*') if p.is_file())
        return tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size)
                     for p in sorted(paths) if p.exists())

    def build_loop():
        nonlocal pdf
        previous = None
        while not stop.is_set():
            current = fingerprint()
            if current != previous:
                previous = current
                with lock:
                    state['message'] = 'ビルド中…'
                process = subprocess.Popen(command, cwd=source.parent, env=env,
                                           start_new_session=True)
                while process.poll() is None:
                    if stop.wait(.2):
                        os.killpg(process.pid, signal.SIGTERM)
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                            process.wait()
                        return
                candidate = output / (source.stem + '.pdf')
                with lock:
                    if process.returncode == 0 and candidate.is_file():
                        pdf = candidate.read_bytes()
                        state.update(message='更新済み · 保存すると自動ビルド',
                                     version=hashlib.sha256(pdf).hexdigest())
                    else:
                        state['message'] = 'ビルド失敗 · ターミナルを確認してください（前回のPDFを表示）'
            stop.wait(.7)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split('?', 1)[0]
            with lock:
                if path == '/':
                    body, mime = PAGE, 'text/html; charset=utf-8'
                elif path == '/status':
                    body, mime = json.dumps(state).encode(), 'application/json'
                elif path == '/report.pdf' and pdf is not None:
                    body, mime = pdf, 'application/pdf'
                else:
                    self.send_error(404)
                    return
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    # Bind before starting the build; a port conflict must not leave a builder running.
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    worker = threading.Thread(target=build_loop, daemon=True)
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Preview: {url}\nCtrl-C で終了', flush=True)
    worker.start()
    try:
        webbrowser.open(url)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()
        worker.join(timeout=5)
