import time
from rss_reader.fetch import fetch_and_store_articles
from rss_reader.database import connect_db, create_table
from rss_reader.config_loader import article_feeds, update_interval_minutes
from rss_reader.logger import logger
import signal

# Control flag to manage scheduler loop
keep_running = True

def signal_handler(sig, frame):
    """
    Gracefully handle termination signals (like Ctrl+C).
    Sets keep_running to False to break the main loop.
    """
    global keep_running
    print("Graceful shutdown requested...")
    keep_running = False

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def update_all_article_feeds():
    """
    Fetch articles from all configured feeds and store them in the database.
    Creates tables if they don't exist.
    """
    logger.info("Fetching new articles...")
    conn = connect_db()

    # Iterate through all configured tables and feeds
    for table_name, feeds in article_feeds.items():
        create_table(conn, table_name)
        for source, url in feeds.items():
            fetch_and_store_articles(url, source, conn, table_name)

    conn.close()
    logger.info("Done fetching articles.")

def run_scheduler(args=None):
    """
    Continuously fetch and store articles at intervals defined in config.
    Supports graceful shutdown via signal.
    """

    interval = args.interval if args and args.interval else update_interval_minutes

    while keep_running:
        try:
            logger.info("Updating articles...")
            update_all_article_feeds()
        except Exception as e:
            logger.error(f"Scheduler error: {e}")

        # Total sleep time between updates
        total_sleep = interval * 60


        # Wait loop with periodic logging
        while total_sleep > 0 and keep_running:
            if total_sleep % 300 == 0:
                mins_remaining = total_sleep // 60
                logger.info(f"Next update in ~{mins_remaining} minutes")

            sleep_chunk = min(5, total_sleep)
            time.sleep(sleep_chunk)
            total_sleep -= sleep_chunk

    logger.info("Scheduler shutdown cleanly.")
