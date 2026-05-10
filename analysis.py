from collections import Counter
import re
import difflib
import nltk
from nltk.corpus import stopwords
from rss_reader.config_loader import custom_english_stopwords, custom_finnish_stopwords
from rss_reader.database import validate_table_name
from rss_reader.logger import logger

try:
    stopwords.words('finnish')
except LookupError:
    nltk.download('stopwords')

# Combine NLTK-provided Finnish stopwords with custom-defined ones
finnish_stopwords = set(stopwords.words('finnish'))
finnish_stop_words = finnish_stopwords.union(custom_finnish_stopwords)


def get_stopwords(table_name):
    """
    Determines which stopword set to use based on the table name.

    Args:
        table_name (str): Name of the database table.

    Returns:
        set: A set of stopwords for the appropriate language/category.
    """
    if "finnish" in table_name.lower():
        return finnish_stop_words
    elif "cyber" in table_name.lower():
        return custom_english_stopwords
    else:
        return set()

def analyze_words(conn, table_name, top_words=10):
    """
    Analyzes word frequency for both content and titles in a database table.

    Args:
        conn: SQLite3 database connection.
        table_name (str): Table to analyze.
        top_words (int): Number of top words to display.
    """
    validate_table_name(table_name)
    stop_words = get_stopwords(table_name)

    cursor = conn.cursor()
    cursor.execute(f"SELECT content, title FROM {table_name}")
    rows = cursor.fetchall()

    # Concatenate all content and titles into separate text blobs
    content_text = " ".join([row[0] for row in rows])
    title_text = " ".join([row[1] for row in rows])

    # Tokenize into word lists
    content_words = content_text.split()
    title_words = title_text.split()

    # Filter out stopwords and short words
    c_filtered = [w for w in content_words if w.lower() not in stop_words and len(w) > 2]
    t_filtered = [w for w in title_words if w.lower() not in stop_words and len(w) > 2]

    # Count word frequency and display results
    c_common = Counter(c_filtered).most_common(100)
    t_common = Counter(t_filtered).most_common(100)

    print(f"\n{top_words} most common words in titles and content:")
    print(f"{'Title':<20} {'Content':<20}")
    print(f"{'-'*20} {'-'*20}")

    for i in range(top_words):
        title_word = f"{t_common[i][0]}: {t_common[i][1]}" if i < len(t_common) else ""
        content_word = f"{c_common[i][0]}: {c_common[i][1]}" if i < len(c_common) else ""
        print(f"{title_word:<20} {content_word:<20}")

def analyze_categories(conn, top_categories=10):
    """
    Analyzes the distribution of article categories within a Finnish news table.

    Args:
        conn: SQLite3 database connection.
        top_categories (int): Number of top categories to display.
    """
    cursor = conn.cursor()
    cursor.execute('''SELECT category, COUNT(*) as count 
                    FROM finnish_news 
                    GROUP BY category 
                    ORDER BY count DESC
                    LIMIT ?;
    ''', (top_categories,))
    c_rows = cursor.fetchall()

    print(f"\nTop 10 most common categories:")
    print(f"{'-'*30}")
    for cate, count in c_rows:
        print(f"Category: {cate}, Count: {count}")

def search_word(conn, s_word, table_name):
    """
    Searches for a specific word within article titles and content.
    Provides fuzzy word suggestions if no exact match is found.

    Args:
        conn: SQLite3 database connection.
        s_word (str): Word to search for.
        table_name (str): Table to search in.
    """
    validate_table_name(table_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT title, link, content, published, category, source FROM {table_name}")
    search_rows = cursor.fetchall()

    skip_category = "cyber" in table_name.lower()

    while True:
        pattern = re.compile(rf"\b{s_word}\b", re.IGNORECASE)
        any_found = False

        for title, link, content, published, category, source in search_rows:
            content_sentences = re.split(r'(?<=[.!?])\s+', content)
            title_match = pattern.search(title)
            content_matches = [s.strip() for s in content_sentences if pattern.search(s)]

            if title_match or content_matches:
                any_found = True
                print(f"\n[SOURCE] {source}")
                print(f"[PUBLISHED] {published}")
                if not skip_category:
                    print(f"[CATEGORY] {category}")
                print(f"[LINK] {link}")
                print(f"[TITLE] {title}")

                if content_matches:
                    for sentence in content_matches[:5]:
                        print(f"[CONTENT MATCH] {sentence}")
                else:
                    print("[NOTE] Word found only in the title. No matches in content.")

        if not any_found:
            print(f"\nNo results found for word: '{s_word}'")

            # Suggest similar words based on content corpus
            all_words = []
            for _, _, content, _, _, _ in search_rows:
                all_words.extend(re.findall(r'\b\w+\b', content.lower()))

            unique_words = set(all_words)
            suggestions = difflib.get_close_matches(s_word.lower(), unique_words, n=5, cutoff=0.7)

            if suggestions:
                print("\nDid you mean one of these?")
                for idx, word in enumerate(suggestions, 1):
                    print(f"[{idx}] {word}")

                try:
                    choice = int(input("Enter number to search with suggested word, 0 to retry new word, or -1 to exit: "))
                    if 1 <= choice <= len(suggestions):
                        s_word = suggestions[choice - 1]
                        continue
                    elif choice == 0:
                        s_word = input("Enter a new word to search for: ").strip()
                        continue
                    elif choice == -1:
                        break
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Invalid input. Try again.")
            else:
                print("No similar words found.")
                new_attempt = input("Enter a new word to search for (or type 'exit' to stop): ").strip()
                if new_attempt.lower() == 'exit':
                    break
                s_word = new_attempt
                continue
        else:
            retry = input("\nSearch another word? (y/n): ").strip().lower()
            if retry == 'y':
                s_word = input("Enter a new word to search for: ").strip()
                continue
            else:
                break

def show_articles_by_tag(conn, table_name, tag):
    """
    Displays articles containing a specific tag from a given table.

    Args:
        conn: SQLite3 database connection.
        table_name (str): Table to search in.
        tag (str): Tag to filter articles by.
    """
    validate_table_name(table_name)
    cursor = conn.cursor()
    query = """
        SELECT id, title, published, source, tags 
        FROM {table}
        WHERE tags LIKE ?
        ORDER BY published DESC
    """.format(table=table_name)

    cursor.execute(query, (f"%{tag}%",))
    articles = cursor.fetchall()

    if articles:
        for article in articles:
            print(f"ID: {article[0]}")
            print(f"Title: {article[1]}")
            print(f"Published: {article[2]}")
            print(f"Source: {article[3]}")
            print(f"Tags: {article[4]}")
            print("-" * 50)
    else:
        print(f"No articles found with tag: {tag}")
