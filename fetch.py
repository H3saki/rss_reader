# Import required modules
import feedparser
from rss_reader.database import insert_article, validate_table_name
from rss_reader.logger import logger
from bs4 import BeautifulSoup
from rss_reader.config_loader import tag_keywords, favorite_keywords

def fetch_and_store_articles(url, source, conn, table_name):
    """
    Fetches articles from an RSS feed, cleans and processes their content,
    tags them based on predefined keywords, saves them to a specified table,
    and adds matching articles to the favorites table based on favorite keywords.
    """
    try:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            # Extract article fields with fallbacks
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            published = entry.get("published", entry.get("updated", "")).strip()

            # Extract content using different possible fields
            content = ""
            if "content" in entry and isinstance(entry.content, list):
                content = entry.content[0].get("value", "")
            elif "summary" in entry:
                content = entry.get("summary", "")
            elif "description" in entry:
                content = entry.get("description", "")

            # Clean HTML content
            clean_content = BeautifulSoup(content, "html.parser").get_text()

            # Tag article based on keywords
            tags = tag_article(title, clean_content, tag_keywords)
            tags_str = ", ".join(tags)

            # Extract category information
            category = ""
            if "tags" in entry and entry.tags:
                category = ", ".join([tag['term'].upper() for tag in entry.tags if 'term' in tag])
            elif "category" in entry:
                category = entry.get("category", "").upper()

            # Insert the article into the database
            insert_article(conn, title, link, published, clean_content, category, source, tags_str, table_name)

            # Check for favorite keywords and save to favorites if found
            article_text = (title + " " + clean_content).lower()
            for keyword in favorite_keywords:
                if keyword in article_text:
                    insert_favorite_article(conn, title, link, published, clean_content, keyword, source)
                    break  # Avoid multiple saves for one article

    except Exception as e:
        logger.error(f"[Error] Failed fetching from {url} ({table_name}): {e}")

def insert_favorite_article(conn, title, link, published, content, keyword, source):
    """
    Inserts an article into the 'favorites' table if it's not already present.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM favorites WHERE link = ?", (link,))
    if cursor.fetchone() is None:
        conn.execute("""
            INSERT INTO favorites (title, link, published, content, keyword, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, link, published, content, keyword, source))
        conn.commit()

def tag_article(title, content, tag_keywords):
    """
    Tags an article by checking if any keywords are found in its title or content.
    Returns a list of matched tags.
    """
    tags = set()  # Avoid duplicate tags
    content_lower = content.lower() if content else ""
    title_lower = title.lower() if title else ""

    for tag, keywords in tag_keywords.items():
        for keyword in keywords:
            if keyword in content_lower or keyword in title_lower:
                tags.add(tag)
    return list(tags)

def get_unique_tags(conn, table_name):
    """
    Retrieves a sorted list of unique tags used in the specified table.
    """
    validate_table_name(table_name)
    cursor = conn.cursor()
    query = f"SELECT tags FROM {table_name} WHERE tags IS NOT NULL AND tags != ''"
    cursor.execute(query)
    tag_rows = cursor.fetchall()

    tags_set = set()
    for (tag_str,) in tag_rows:
        tags = [tag.strip() for tag in tag_str.split(",")]
        tags_set.update(tags)

    return sorted(tags_set)

def retag_existing_articles(conn, table_name, tag_keywords):
    """
    Retags all existing articles in a given table using the current set of tag keywords.
    """
    validate_table_name(table_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, title, content FROM {table_name}")
    articles = cursor.fetchall()

    for article_id, title, content in articles:
        tags = tag_article(title, content, tag_keywords)
        tags_str = ", ".join(tags)
        conn.execute(
            f"UPDATE {table_name} SET tags = ? WHERE id = ?",
            (tags_str, article_id)
        )
    conn.commit()

def save_favorites_from_existing_articles(conn, table_name, favorite_keywords):
    """
    Scans existing articles for favorite keywords and saves matching articles
    to the favorites table.
    """
    validate_table_name(table_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, title, link, published, content, source FROM {table_name}")
    articles = cursor.fetchall()

    favorite_keywords_lower = [kw.lower() for kw in favorite_keywords]

    for article_id, title, link, published, content, source in articles:
        article_text = (title + " " + content).lower()
        for keyword in favorite_keywords_lower:
            if keyword in article_text:
                insert_favorite_article(conn, title, link, published, content, keyword, source)
                break  # Avoid inserting same article multiple times

    conn.commit()


if __name__ == "__main__":
    from rss_reader.database import connect_db


    # Connect to the database
    conn = connect_db()

    # Specify tables to process
    table_names = ["cyber_news", "finnish_news"]
    for table_name in table_names:
        # Retag existing articles with updated keywords
        retag_existing_articles(conn, table_name, tag_keywords)

        # Save favorites from existing articles
        save_favorites_from_existing_articles(conn, table_name, favorite_keywords)

        print("Retagging and favorite extraction completed")
