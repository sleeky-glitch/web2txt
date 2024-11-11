import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

st.set_page_config(page_title="Website Crawler and Text Extractor")
st.title("Website Crawler and Text Extractor")

# Input for URL and Depth of Crawl
url = st.text_input("Enter the website URL:")
max_depth = st.number_input("Depth of Crawl (number of levels)", min_value=1, max_value=10, value=2)
visited_pages = set()  # Set to keep track of visited URLs to avoid duplicates

def extract_text_from_url(url):
    """Extract text content from a single URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the webpage content
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract text content
        text = soup.get_text(separator="\n")
        
        return text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return None

def crawl_and_extract_text(url, depth=1):
    """Recursively crawl and extract text up to a specified depth."""
    if depth > max_depth:
        return ""

    # Avoid revisiting the same URL
    if url in visited_pages:
        return ""
    visited_pages.add(url)

    # Extract and display text from the current page
    page_text = extract_text_from_url(url)
    all_text = page_text if page_text else ""

    # Recursively find links on the page and crawl them
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all hyperlinks on the page
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            full_url = urljoin(url, href)  # Ensure the link is absolute

            # Check if the URL is within the same domain
            if urlparse(full_url).netloc == urlparse(url).netloc:
                # Recursive call for the next page
                all_text += crawl_and_extract_text(full_url, depth + 1)
                time.sleep(1)  # Add a delay to avoid overloading the server
    except Exception as e:
        st.error(f"Error crawling {url}: {e}")

    return all_text

# Add a button to trigger the extraction and crawling process
if st.button("Search"):
    if url:
        st.write("Crawling and extracting text from the website...")
        crawled_text = crawl_and_extract_text(url)
        
        if crawled_text:
            # Display the extracted text in an expandable section
            with st.expander("Show Extracted Text"):
                st.text_area("Crawled Website Text Content", crawled_text, height=400)
    else:
        st.warning("Please enter a URL to search.")
