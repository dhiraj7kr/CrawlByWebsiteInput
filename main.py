import os
import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

def sanitize_filename(filename, fallback="scraped_website"):
    """
    Removes illegal characters from strings to make them safe for Windows/Linux filenames.
    """
    if not filename or not filename.strip():
        return fallback
    clean_name = re.sub(r'[\\/*?:"<>|]', "", filename.strip())
    clean_name = re.sub(r'[\s\-]+', "_", clean_name)
    return clean_name[:100].lower().strip("_")

def generate_readme(data, output_dir, file_base_name):
    """
    Generates a high-quality Markdown README summarizing the scraped data.
    """
    readme_path = os.path.join(output_dir, f"{file_base_name}_README.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format a list of files if any were found
    files_section = "No downloadable files detected on this page."
    if data['downloadable_files']:
        files_list = "\n".join([f"* [{os.path.basename(f) or 'Download Link'}]({f})" for f in data['downloadable_files'][:15]])
        files_section = f"Here are the primary files discovered on this page:\n\n{files_list}"
        if len(data['downloadable_files']) > 15:
            files_section += f"\n\n*(...and {len(data['downloadable_files']) - 15} more listed in the JSON report)*"

    # Format sample links
    links_section = "No external/internal links found."
    if data['all_links']:
        links_list = "\n".join([f"* {link}" for link in data['all_links'][:10]])
        links_section = f"{links_list}\n\n*(See `{file_base_name}.json` for the complete list of {len(data['all_links'])} links)*"

    readme_content = f"""# 🌐 Scraping Report: {data['title']}

**Target URL:** [{data['url']}]({data['url']})  
**Scraping Timestamp:** `{timestamp}`  

---

## 📊 Executive Summary

This package contains the automated extraction logs, raw text content, and media paths harvested from **{data['title']}**. 

| Resource Type | Total Harvested |
| :--- | :---: |
| 🖼️ **Images & Responsive Sources** | `{data['summary_counts']['images_found']}` |
| 💾 **Downloadable Files** *(PDFs, Docs, Archives)* | `{data['summary_counts']['files_found']}` |
| 🔗 **Webpage Links** *(Internal & External)* | `{data['summary_counts']['total_links']}` |
| 📜 **JavaScript Files** | `{data['summary_counts']['scripts']}` |
| 🎨 **Stylesheets** | `{data['summary_counts']['stylesheets']}` |

---

## 💾 Discovered Files & Documents
{files_section}

---

## 🔗 Sample Navigation Links
{links_section}

---

## 📂 About These Files

Your extraction output generated three distinct files in this directory:
1. **`{file_base_name}_README.md`** — This executive summary document.
2. **`{file_base_name}.json`** — The complete, machine-readable dataset containing every absolute URL, script path, and media link.
3. **`{file_base_name}.txt`** — The stripped, clean text content of the webpage (free of HTML, navigation menus, and JavaScript).

---

*Generated automatically by SiteHarvester Python Utility.*
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content.strip())
        
    return readme_path

def scrape_website(url, output_dir="scraped_output"):
    """
    Scrapes a website for all text content, images, downloadable files, and links.
    Saves the extracted data using the webpage's title as the file name.
    """
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
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Extract Page Title & Create Safe Filename Base
    raw_title = soup.title.string.strip() if soup.title and soup.title.string else ""
    domain_fallback = urlparse(url).netloc.replace(".", "_")
    
    file_base_name = sanitize_filename(raw_title, fallback=domain_fallback)
    display_title = raw_title if raw_title else "No Title Found"
    
    print(f"[*] Page Title Detected: '{display_title}'")
    print(f"[*] Base Filename: {file_base_name}.*")

    # 2. Extract Visible Text Content (stripping scripts and styles)
    for element in soup(["script", "style", "nav", "footer", "noscript"]):
        element.extract()
    
    raw_text = soup.get_text(separator="\n")
    clean_text = "\n".join([line.strip() for line in raw_text.splitlines() if line.strip()])

    # 3. Extract All Image Links
    images = set()
    for img in soup.find_all(["img", "source"]):
        src = img.get("src") or img.get("srcset")
        if src:
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
        clean_url = full_url.split("#")[0]
        if clean_url.endswith("/"):
            clean_url = clean_url[:-1]
        
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
        "title": display_title,
        "summary_counts": {
            "images_found": len(images),
            "files_found": len(files),
            "total_links": len(all_links),
            "scripts": len(scripts),
            "stylesheets": len(stylesheets)
        },
        "images": sorted(list(images)),
        "downloadable_files": sorted(list(files)),
        "all_links": sorted(list(all_links)),
        "scripts": scripts,
        "stylesheets": stylesheets
    }

    # Save to JSON using the sanitized title
    json_path = os.path.join(output_dir, f"{file_base_name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # Save clean text to TXT using the sanitized title
    txt_path = os.path.join(output_dir, f"{file_base_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {display_title}\nURL: {url}\n{'='*50}\n\n{clean_text}")

    # Generate and save the README summary
    readme_path = generate_readme(data, output_dir, file_base_name)

    print(f"\n[+] Extraction Complete!")
    print(f"    - Extracted {len(images)} images")
    print(f"    - Extracted {len(files)} downloadable files")
    print(f"    - Extracted {len(all_links)} webpage links")
    print(f"    - Saved JSON report:   {json_path}")
    print(f"    - Saved text content:  {txt_path}")
    print(f"    - Saved README report: {readme_path}")

    return data

if __name__ == "__main__":
    target_url = input("Enter website URL (e.g., https://example.com): ").strip()
    if not target_url.startswith("http"):
        target_url = "https://" + target_url
        
    scrape_website(target_url)