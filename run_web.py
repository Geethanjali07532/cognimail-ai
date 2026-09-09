"""
CogniMail AI - Web Cockpit Server Launcher
Launches FastAPI backend serving both REST API endpoints and the rich HTML5/CSS3/JS Web UI.

Usage:
    python run_web.py
    python run_web.py --port 8000 --no-browser
"""

import os
import sys
import time
import argparse
import webbrowser
import threading
import uvicorn

# Ensure terminal handles UTF-8
sys.stdout.reconfigure(encoding='utf-8')


import socket

def get_local_ip():
    """Detect the local machine's IP address on the Wi-Fi / Local Area Network."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def open_browser_delayed(url: str, delay: float = 4.5):
    """Open default web browser after server initializes and pre-warms AI models."""
    def _open():
        time.sleep(delay)
        print(f"[BROWSER] Launching CogniMail AI Web Cockpit at: {url}")
        webbrowser.open(url)
    t = threading.Thread(target=_open, daemon=True)
    t.start()


def main():
    parser = argparse.ArgumentParser(description="CogniMail AI Web Cockpit Runner")
    parser.add_argument("--host", default="0.0.0.0", help="Host IP to bind (default: 0.0.0.0 for LAN/mobile access)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code change")
    args = parser.parse_args()

    local_ip = get_local_ip()
    local_url = f"http://localhost:{args.port}"
    mobile_url = f"http://{local_ip}:{args.port}"

    print("=" * 75)
    print("      COGNIMAIL AI — ENTERPRISE EMAIL INTELLIGENCE WEB COCKPIT")
    print("=" * 75)
    print(f"  ● Local PC URL:       {local_url}")
    print(f"  ● Mobile (Same Wi-Fi): {mobile_url}")
    print(f"  ● Swagger REST API:   {local_url}/docs")
    print(f"  ● Health Check:       {local_url}/api/health")
    print(f"  ● Static UI Root:     {os.path.join(os.path.dirname(__file__), 'static')}")
    print("=" * 75)
    print("Pre-warming all 15 AI inference models in memory (Category, Sentiment, Priority, NER, Summarizer, Smart Reply, Security)...")

    if not args.no_browser:
        open_browser_delayed(local_url)

    # Start Uvicorn Server
    uvicorn.run(
        "app_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
