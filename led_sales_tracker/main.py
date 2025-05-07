#!/usr/bin/env python3
"""
Entry point: chooses display backend, periodically pulls data and renders.
"""
import time
import logging
import signal
import sys
from .config import REFRESH_INTERVAL
from datetime import datetime
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

    SEGMENTS = 64  # Width of the matrix
    SEGMENT_TIME = REFRESH_INTERVAL / SEGMENTS  # Time per segment

    days = 63
    while True:
        try:
            units_data = client.get_sales_data(metric_type='units', days=days)
            print(f"\nTotal units sold for 14 days: {units_data['total_units']}")

            disp.clear()
            current_time = datetime.now().strftime("%H:%M")  # or use %I:%M %p for 12-hr format
            msg = f"{units_data['total_units']}   {current_time}"
            # msg = f"{units_data['total_units']} {days}d"
            
            for day in units_data['daily_units']:
                print(f"{day['date']}: {day['units_sold']} units")

            series = []
            for i, day in enumerate(units_data['daily_units']):
                x = i
                y = -day['units_sold']  # Negative y to "go up" if (0,0) is top-left
                series.append((x, y))

            # Now draw it
            disp.draw_series(series, x=0, y=32, colour=(0, 255, 0))

            disp.draw_text(msg, x=1, y=1, colour=(0,255,0))
            disp.push()
            
            # Now handle the loading bar updates
            start_time = time.time()
            for segment in range(SEGMENTS + 1):  # +1 to include waiting for the last segment
                current_time = time.time()
                elapsed = current_time - start_time
                target_time = segment * SEGMENT_TIME
                
                if segment > 0:  # Only draw if we're past the first segment
                    if elapsed < target_time:
                        # Wait until it's time for the next segment
                        time.sleep(target_time - elapsed)
                    disp.set_pixel(segment-1, 0, (100, 100, 100))  # Add just the newest segment
                    disp.push()

                # If we've filled the entire bar, exit the loop
                if segment >= SEGMENTS:
                    break
                    
                # Check if we need to sleep to reach the next segment time
                current_time = time.time()
                elapsed = current_time - start_time
                next_segment_time = (segment + 1) * SEGMENT_TIME
                if elapsed < next_segment_time:
                    time.sleep(next_segment_time - elapsed)
        except Exception as e:
            log.error(f"Error: {e}")
            disp.clear()
            disp.draw_text("Error", x=1, y=1, colour=(255, 255, 255))
            disp.push()
            time.sleep(5)

if __name__ == "__main__":
    main()