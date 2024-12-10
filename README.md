<a name="readme-top"></a>

<!-- PROJECT LOGO -->

# Pulitizer Web Scraper

This Python script scrapes Pulitzer Prize-winning photography data and images from the official Pulitzer Prize website. It collects information such as image URLs, captions, photographers, organizations, and locations for select photo categories, then saves the data as a CSV file and downloads the images locally.

## How It Works
1. Initialize Web Session: Uses curl_cffi to start a browser-like session to avoid bot detection.
2. Download Global Vocabulary: Pulls a JSON file (global.json) from the Pulitzer website to map category and year identifiers (TID) to human-readable names.
3. Get Winner Page IDs (NIDs): Scrapes the NID values (IDs for individual award-winning photos) for categories like Feature Photography, Breaking News Photography, and Spot News Photography.
4. Extract Winner Details: For each NID, the script gathers the photographer's name, organization, caption, and image URL. It uses spaCy's NLP model to extract information from the caption.
5. Save Image Data: All extracted data (image URLs, captions, and photographer info) is saved to winner_data.csv.
6. Download Images: Images are downloaded and saved in the images folder.

## Files Created
`data/globalVocab.json`: JSON file with category-year mappings.
`data/winner_data.csv`: CSV file with image data (URL, category, year, caption, etc.).
`images/`: Directory containing all the images from Pulitzer Prize-winning photographs.

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#description">Description</a></li>
    </li>
    <li>
      <a href="#built-with">Built With</a></li>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#resources">Resources</a></li>
  </ol>
</details>

## Built With

### Python Libraries:
<ul>
<li>curl_cffi - Browser-like session for scraping.
<li>requests - Fetches image content.
<li>pandas - Exports data to CSV.
<li>Pillow (PIL) - Processes and saves images.
<li>spaCy (https://spacy.io/) - Extracts names, organizations, and locations from captions.
<li>tqdm - Progress bar for tracking scraping status.
</ul>

## Getting Started

### Prerequisites

- Python

### Installation

Create virtual environment

Install the Python packages from `requirements.txt`

```
pip install -r requirements.txt
```

Alternatively, you can download each required package individually:

```
pip install curl-cffi requests pandas pillow spacy
python -m spacy download en_core_web_lg
```

## Usage

To run the project locally run the command:
```
python scraper.py
```

## Resources

<ul>
    <li>[Save images from url](https://stackoverflow.com/questions/30229231/python-save-image-from-url)
    <li>[Basic web scrape example](https://oxylabs.io/blog/python-web-scraping)
    <li>[Scrape image from website](https://oxylabs.io/blog/scrape-images-from-website)
    <li>[Get data from server API](https://www.youtube.com/watch?v=ji8F8ppY8bs&t=767s)
    <li>[Spacy usage](https://www.geeksforgeeks.org/python-named-entity-recognition-ner-using-spacy/)
</ul>

<!-- To Do List -->
<!--
- Debug caption split
- image file names saved as name.jpg.png
- manually check images against csv file
- make more efficient
-->

