import os
import json
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

def scrape_website(url, output_dir="scraped_output"):
    """
    Scrapes a website for all text content, images, downloadable files, and links.
    Saves the extracted data into an organized JSON file and text file.
    """
    # Use a standard browser User-Agent to prevent 403 Forbidden errors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"[*] Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    domain = urlparse(url).netloc.replace(".", "_")
    
    # 1. Extract Page Title & Metadata
    title = soup.title.string.strip() if soup.title else "No Title Found"
    
    # 2. Extract Visible Text Content (stripping scripts and styles)
    for element in soup(["script", "style", "nav", "footer", "noscript"]):
        element.extract()
    
    raw_text = soup.get_text(separator="\n")
    # Clean up empty lines and whitespace
    clean_text = "\n".join([line.strip() for line in raw_text.splitlines() if line.strip()])

    # 3. Extract All Image Links (including <source> for responsive images)
    images = set()
    for img in soup.find_all(["img", "source"]):
        src = img.get("src") or img.get("srcset")
        if src:
            # Handle srcset containing multiple URLs
            first_url = src.split(",")[0].split()[0]
            images.add(urljoin(url, first_url))

    # 4. Extract Downloadable Files & General Links
    file_extensions = (
        '.pdf', '.zip', '.rar', '.tar', '.gz', '.7z', 
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
        '.csv', '.txt', '.mp3', '.mp4', '.avi', '.mov', '.exe', '.apk'
    )
    
    files = set()
    all_links = set()
    
    for a_tag in soup.find_all("a", href=True):
        full_url = urljoin(url, a_tag["href"])
        # Remove URL fragments (#section)
        clean_url = full_url.split("#")[0]
        
        if clean_url.lower().endswith(file_extensions):
            files.add(clean_url)
        elif clean_url.startswith("http"):
            all_links.add(clean_url)

    # 5. Extract Scripts and Stylesheets
    scripts = [urljoin(url, script["src"]) for script in soup.find_all("script", src=True)]
    stylesheets = [urljoin(url, link["href"]) for link in soup.find_all("link", rel="stylesheet", href=True)]

    # Compile data dictionary
    data = {
        "url": url,
        "title": title,
        "summary_counts": {
            "images_found": len(images),
            "files_found": len(files),
            "total_links": len(all_links),
            "scripts": len(scripts),
            "stylesheets": len(stylesheets)
        },
        "images": list(images),
        "downloadable_files": list(files),
        "all_links": list(all_links),
        "scripts": scripts,
        "stylesheets": stylesheets
    }

    # Save to JSON
    json_path = os.path.join(output_dir, f"{domain}_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # Save clean text to TXT
    txt_path = os.path.join(output_dir, f"{domain}_content.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {title}\nURL: {url}\n{'='*50}\n\n{clean_text}")

    print(f"\n[+] Extraction Complete!")
    print(f"    - Extracted {len(images)} images")
    print(f"    - Extracted {len(files)} downloadable files")
    print(f"    - Extracted {len(all_links)} webpage links")
    print(f"    - Saved JSON report to: {json_path}")
    print(f"    - Saved text content to: {txt_path}")

    return data

if __name__ == "__main__":
    # Replace with the website you want to scrape
    target_url = input("Enter website URL (e.g., https://example.com): ").strip()
    if not target_url.startswith("http"):
        target_url = "https://" + target_url
        
    scrape_website(target_url)