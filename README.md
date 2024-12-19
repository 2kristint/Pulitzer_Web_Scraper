# Pulitzer Web Scraper

This Jupyter Notebook/Python script scrapes Pulitzer Prize-winning photography data and images from the official Pulitzer Prize website. It collects information such as image URLs, captions, photographers, organizations, and locations for select photo categories, then saves the data as a CSV file and downloads the images locally.

## How It Works
1. Initialize Web Session: Uses curl_cffi to start a browser-like session to avoid bot detection.
2. Download Global Vocabulary: Pulls a JSON file (global.json) from the Pulitzer website to map category and year identifiers (TID) to human-readable names.
3. Get Winner Page IDs (NIDs): Scrapes the NID values (IDs for individual award-winning photos) for categories like Feature Photography, Breaking News Photography, and Spot News Photography.
4. Extract Winner Details: For each NID, the script gathers the photographer's name, organization, caption, and image URL. It uses spaCy's NLP model to extract information from the caption.
5. Save Image Data: All extracted data (image URLs, captions, and photographer info) is saved to winner_data.csv.
6. Download Images: Images are downloaded and saved in the images folder.

## Files Created

`data/globalVocab.json`: JSON file with category-year mappings <br>
`data/winner_data.csv`: CSV file with image data (URL, category, year, caption, etc.) <br>
`images/`: Directory containing all the images from Pulitzer Prize-winning photographs <br>

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

## Running scraper.py python file

### Prerequisites

- Python

### Installation

Create virtual environment (recommended)

Install the Python packages from `requirements.txt`

```
pip install -r requirements.txt
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


