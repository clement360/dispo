#!/usr/bin/env python3
"""
Entry point: chooses display backend, periodically pulls data and renders.
"""
import time
import logging
import signal
import sys
from .config import REFRESH_INTERVAL
from .display import get_display
from .api.amazon_client import AmazonClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

log = logging.getLogger("main")

def main():
    disp = get_display()
    disp.initialize()

    client = AmazonClient()

    def cleanup_and_exit(sig, frame):
        log.info("Cleaning up...")
        disp.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    while True:
        data = client.get_sales_data()
        disp.clear()
        msg = f"T:{data['sales_today']} Y:{data['sales_yesterday']}"
        disp.draw_text(msg, x=1, y=12, colour=(0,255,0))
        disp.push()
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main()