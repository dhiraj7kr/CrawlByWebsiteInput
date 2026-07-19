# CrawlByWebsiteInput

<div align="center">
  
# 🕸️ SiteHarvester
**A robust, lightweight Python utility to extract everything from a webpage.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)]()
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4-green?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)]()

</div>

---

## ⚡ Overview

SiteHarvester is a targeted web scraping script that instantly digests a target URL and pulls out all meaningful data. Instead of digging through raw HTML, this tool cleanly separates visible text, images, downloadable files, and navigational links, exporting everything into organized JSON and TXT formats.

## ✨ Key Features

*   **🧹 Smart Text Extraction:** Automatically strips out noisy `<script>`, `<style>`, and navigation elements to give you pure readable content.
*   **🖼️ Media & File Discovery:** Identifies and extracts absolute URLs for images, stylesheets, and downloadable files (PDFs, ZIPs, Office docs, etc.).
*   **🔗 Auto-Resolving URLs:** Converts messy relative paths (`/assets/img.png`) into fully qualified, clickable URLs.
*   **🛡️ Anti-Blocking Headers:** Mimics standard Google Chrome requests to bypass basic `403 Forbidden` bot-protections.
*   **📁 Structured Export:** Automatically generates both a beautifully formatted text file for reading and a structured JSON file for programmatic use.

---

## 🚀 Getting Started

### Prerequisites

You need Python 3.8+ installed on your machine. Install the required dependencies using pip:

```bash
pip install requests beautifulsoup4
