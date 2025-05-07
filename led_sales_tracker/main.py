#!/usr/bin/env python3
"""
Entry point: chooses display backend, periodically pulls data and renders.
"""
import time
import logging
import signal
import sys
from datetime import datetime
from .config import REFRESH_INTERVAL # Assuming this is the duration for the loading bar animation
from .display import get_display
from .api.amazon_client import AmazonClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

log = logging.getLogger("main_app") # Changed logger name slightly for clarity

# --- Helper Rendering Functions ---

def _render_sales_data_on_display(disp, units_data):
    """Renders the sales data and current time on the display."""
    disp.clear()
    current_time_str = datetime.now().strftime("%H:%M")  # or %I:%M%p for 12-hr
    msg = f"{units_data.get('total_units', 'N/A')}   {current_time_str}"
    
    series = []
    # Ensure daily_units exists and is a list
    daily_units_list = units_data.get('daily_units', [])
    if isinstance(daily_units_list, list):
        for i, day_data in enumerate(daily_units_list):
            # Make sure 'units_sold' key exists, default to 0 if not
            units_sold = day_data.get('units_sold', 0)
            x = i
            y = -units_sold  # Negative y to "go up" if (0,0) is top-left
            series.append((x, y))

    # Draw the sales series (e.g., a line graph)
    # Assuming y=32 is a baseline for the graph on your display
    disp.draw_series(series, x=0, y=32, colour=(0, 255, 0)) # Green

    # Draw the text message (total units and time)
    disp.draw_text(msg, x=1, y=1, colour=(0, 255, 0)) # Green
    disp.push() # Push the rendered sales data to the display immediately

def _animate_loading_bar(disp, total_bar_segments, total_bar_duration, animation_start_ref_time):
    """
    Animates a loading bar over a specified duration.
    The animation itself will take 'total_bar_duration'.
    """
    if total_bar_segments <= 0:
        return # Nothing to animate

    time_per_segment = total_bar_duration / total_bar_segments

    for current_segment_num in range(total_bar_segments + 1): # Loop from 0 to total_bar_segments
        # Calculate elapsed time since the animation reference start
        elapsed_since_ref_start = time.time() - animation_start_ref_time
        
        # When should the (current_segment_num)-th step of logic ideally execute?
        # For drawing pixel N, we consider it at step N+1.
        target_time_for_this_step = current_segment_num * time_per_segment

        if current_segment_num > 0:  # Only draw if we're past the first conceptual segment (i.e., drawing pixel 0 onwards)
            pixel_to_draw_index = current_segment_num - 1 # Pixels are 0-indexed

            # Wait if we are too early for this step's pixel drawing
            if elapsed_since_ref_start < target_time_for_this_step:
                sleep_duration = target_time_for_this_step - elapsed_since_ref_start
                if sleep_duration > 0: # Defensive check for tiny negative sleeps
                    time.sleep(sleep_duration)
            
            disp.set_pixel(pixel_to_draw_index, 0, (100, 100, 100))  # Grey pixel at y=0
            disp.push() # Push the new segment of the loading bar

        # If all segments (pixels 0 to total_bar_segments-1) have been drawn
        if current_segment_num >= total_bar_segments:
            break # Exit the loop
            
        # Recalculate elapsed time after drawing and potential sleep
        elapsed_after_draw = time.time() - animation_start_ref_time
        
        # Determine when the next segment's logic should ideally start
        target_time_for_next_step_processing = (current_segment_num + 1) * time_per_segment
        
        # Sleep until it's time to process the next segment
        if elapsed_after_draw < target_time_for_next_step_processing:
            sleep_duration_for_next = target_time_for_next_step_processing - elapsed_after_draw
            if sleep_duration_for_next > 0: # Defensive check
                time.sleep(sleep_duration_for_next)

def _render_error_on_display(disp, error_text="Error"):
    """Clears display and shows an error message."""
    disp.clear()
    disp.draw_text(error_text, x=1, y=1, colour=(255, 0, 0)) # Red
    disp.push()

# --- Main Application Logic ---

def main():
    disp = get_display()
    disp.initialize()

    amazon_api_client = AmazonClient()

    def cleanup_and_exit(sig, frame):
        log.info("Signal received. Cleaning up display and exiting...")
        disp.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    # Configuration for data fetching and display
    DAYS_OF_DATA_TO_FETCH = 63  # Corresponds to graph width potentially
    
    # Configuration for the loading bar animation
    # Assuming SEGMENTS means the number of pixels for the loading bar (e.g., display width)
    LOADING_BAR_PIXEL_WIDTH = 64
    # REFRESH_INTERVAL from config is assumed to be the desired duration for the loading bar animation
    LOADING_BAR_ANIMATION_DURATION = REFRESH_INTERVAL 

    log.info(f"Application started. Data refresh cycle will involve a loading bar animation of {LOADING_BAR_ANIMATION_DURATION}s.")

    while True:
        try:
            # 1. Fetch sales data
            log.info(f"Fetching sales data for the last {DAYS_OF_DATA_TO_FETCH} days...")
            units_data = amazon_api_client.get_sales_data(metric_type='units', days=DAYS_OF_DATA_TO_FETCH)
            log.info(f"Data received. Total units: {units_data.get('total_units', 'N/A')}")

            # 2. Render the fetched sales data on the display
            _render_sales_data_on_display(disp, units_data)
            
            # 3. Animate the loading bar for the configured duration
            # This call will block for approx. LOADING_BAR_ANIMATION_DURATION seconds.
            loading_bar_animation_start_time = time.time()
            _animate_loading_bar(disp, LOADING_BAR_PIXEL_WIDTH, LOADING_BAR_ANIMATION_DURATION, loading_bar_animation_start_time)
            log.debug("Loading bar animation complete.")

        except Exception as e:
            log.error(f"An error occurred in the main loop: {e}", exc_info=True)
            _render_error_on_display(disp, "ERR") # Keep error short for small displays
            # Wait for a bit before trying the whole loop again to avoid spamming APIs on persistent errors
            time.sleep(10) # Increased sleep on error

if __name__ == "__main__":
    main()