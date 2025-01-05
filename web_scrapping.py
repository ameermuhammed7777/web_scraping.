import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def resolve_redirect(link):
    try:
        response = requests.get(link, allow_redirects=True)
        response.raise_for_status()
        return response.url  
    except requests.exceptions.RequestException:
        return link 

def fetch_read_more_links(base_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    read_more_links = set()
    
    for link in links:
        if link.text.strip().lower() == "read more":
            href = link.get('href')
            full_url = urljoin(base_url, href)
            resolved_url = resolve_redirect(full_url)
            read_more_links.add(resolved_url)
    
    return read_more_links


def fetch_file_links(base_url, file_extensions=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    file_links = set()
    for link in links:
        href = link.get('href')
        full_url = urljoin(base_url, href)
        if file_extensions:
            if any(full_url.endswith(ext) for ext in file_extensions):
                file_links.add(full_url)
        else:
            file_links.add(full_url)
    return file_links


def main():
    st.title("PDF Link Fetcher From Articles")
    
    featured_topic = st.sidebar.selectbox(
        "Featured Topic",
        ['macro', 'portfolio-construction', 'equities', 'fixed-income', 'commodities', 
         'private-markets', 'hedge-funds', 'indexing-passive', 'emerging-markets', 
         'thematic-megatrends', 'sustainability', 'industry']
    )
    # page = st.sidebar.number_input("Enter Page Number", min_value=1, max_value=50, value=1)
    page=1
    sort_by=st.sidebar.selectbox("Sort By All",['All','latest','featured','trending'])

    base_url = "https://marketsrecon.com"

    if 'article_links' not in st.session_state:
        st.session_state.article_links = []

    if st.button("Fetch Article Links"):
        if not featured_topic:
            st.error("Please select a valid topic.")
        else:
            if sort_by=='All':
                full_url = urljoin(base_url, f"/category/{featured_topic}-1?page={page}")

            elif sort_by=='latest':
                full_url=urljoin(base_url,sort_by)
            elif sort_by=='featured':
                full_url=urljoin(base_url,sort_by)
            elif sort_by=='trending':
                full_url=urljoin(base_url,sort_by)
            if full_url.strip() == "":
                st.error("Please enter a valid URL.") 
            else:
                links = fetch_read_more_links(full_url) 
                if not links:
                    st.warning("No Article links found.")
                else:
                    st.success("'Article' links fetched successfully!")
                    st.session_state.article_links = list(links)  
                    # for link in links:
                    #     st.write(f"[{link}]({link})")

    # Display fetched article links if they exist
    if st.session_state.article_links:
        for url in st.session_state.article_links:
            furl=url.replace("https://marketsrecon.com/content/","")
            link="https://marketsrecon.com/redirect?name=app_content&parameters%5Bslug%5D="+furl
            st.write(f"[{link}]({link})")
    
    st.write("Enter a URL of Article to Fetch PDF.")
    url = st.text_input("Enter URL", "")
    file_extensions = ['.pdf', '.xlsx', '.docx', '.zip', '.csv', '.jpg', '.mp4', '.rar', '.json', '.py']

    if st.button("Fetch Pdf File"):
        if url.strip() == "":
            st.error("Please enter a valid URL.")
        else:
            st.write("Fetching file links...")
            files = fetch_file_links(url, file_extensions)
            if not files:
                st.warning("No files found.")
            else:
                st.success("Files fetched successfully!")
                for file_url in files:
                    st.write(f"[{file_url}]({file_url})")

if __name__ == "__main__":
    main()
