# Import functions from different modules of the rss_reader package
from rss_reader.analysis import analyze_categories, analyze_words, search_word, show_articles_by_tag
from rss_reader.database import create_table, connect_db, backup_database
from rss_reader.scheduler import run_scheduler
from rss_reader.fetch import fetch_and_store_articles, get_unique_tags, save_favorites_from_existing_articles
from rss_reader.config_loader import article_feeds, favorite_keywords
# import argparse



# Connect to SQLite database
conn = connect_db()

def manual_run():
    """
    Manually fetch and store articles from all feeds listed in the config.

    - Loops through each table and its associated RSS feeds.
    - Creates table if it doesn’t exist.
    - Fetches new articles and stores them in the database.
    """
    print("[UPDATE] Fetching new articles...")
    for table_name, feeds in article_feeds.items():
        create_table(conn, table_name)  # Ensure the table exists
        save_favorites_from_existing_articles(conn, table_name, favorite_keywords)
        for source, url in feeds.items():
            fetch_and_store_articles(url, source, conn, table_name)
    print("[UPDATE] Done fetching articles.")
    conn.close()

def analyze():
    # Enter analysis mode, with three sub-options
    analysis_mode = input(
        "Choose analysis mode: [1] Search with specific word [2] Search top words [3] Search with tags: ")

    if analysis_mode == "1":
        # Search for a specific word within a chosen table
        which_a = (input("Search specific word from [1] Finnish news [2] Cyber news: "))
        if which_a == "1":
            s_word = input("What word do you want to search for? ")
            search_word(conn, s_word, "finnish_news")
        elif which_a == "2":
            s_word = input("What word do you want to search for? ")
            search_word(conn, s_word, "cyber_news")
        else:
            print("Invalid input")

    elif analysis_mode == "2":
        # Analyze most used words and categories
        which_article = input("Analyze [1] Finnish news [2] Cyber news: ")
        if which_article == "1":
            w_user_input = input("How many most used words do you want to display? ")
            top_words = int(w_user_input) if w_user_input.isdigit() else 10

            c_user_input = input("How many most common categories do you want to display? ")
            top_categories = int(c_user_input) if c_user_input.isdigit() else 10

            analyze_words(conn, "finnish_news", top_words)
            analyze_categories(conn, top_categories)

        elif which_article == "2":
            user_input = input("How many most used words do you want to display? ")
            top_words = int(user_input) if user_input.isdigit() else 10

            analyze_words(conn, "cyber_news", top_words)
        else:
            print("Invalid input")

    elif analysis_mode == "3":
        # List and select articles by tag
        table = input("Choose table [1] cyber_news [2] finnish_news: ")
        if table == "1":
            table_name = "cyber_news"
        elif table == "2":
            table_name = "finnish_news"
        else:
            print("Invalid input")

        # Fetch and list unique tags for selected table
        tags = get_unique_tags(conn, table_name)
        if tags:
            print("\nAvailable tags:")
            for tag in tags:
                print(f"- {tag}")
        else:
            print("No tags found in this table.")

        # Prompt for a tag to display related articles
        tag = input("\nEnter a tag to view articles: ").strip().upper()
        show_articles_by_tag(conn, table_name, tag)

    else:
        print("Invalid analysis option.")

def main():
    # Mode selector: Manual run, Scheduler, or Analysis
    mode = input("Choose mode: [1] Manual Run  [2] Scheduler  [3] Analysis: ")

    if mode == "1":
        manual_run()

    elif mode == "2":
        # Start the article fetching scheduler (runs periodically)
        run_scheduler()

    elif mode == "3":
        analyze()

    else:
        print("Invalid option.")


    #TEST
# def main():
#     parser = argparse.ArgumentParser(description="RSS_READER/ANALYZER")
#     subparser = parser.add_subparsers(dest='command')
#     subparser.required = True
#
#     parser_manual_run = subparser.add_parser('run', help='Do a manual run')
#     parser_manual_run.set_defaults(func=lambda args: manual_run())
#
#     parser_scheduler = subparser.add_parser('scheduler', help='Does scheduled fetches every 30min')
#     parser_scheduler.add_argument('--interval', type=int, help='Update interval in minutes')
#     parser_scheduler.set_defaults(func=run_scheduler)
#
#     parser_analyze = subparser.add_parser('analyze', help='Analyze articles')
#     parser_analyze.set_defaults(func=lambda args: analyze())
#
#     parser_backup_db = subparser.add_parser('backup', help='Creates backup of the database')
#     parser_backup_db.set_defaults(func=lambda args: backup_database())


    #
    # args = parser.parse_args()
    # args.func(args)

if __name__ == "__main__":
    main()
