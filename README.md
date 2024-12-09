# Pulitzer_Web_Scraper
<a name="readme-top"></a>

<!-- PROJECT LOGO -->

# Pulitizer Web Scraper

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#built-with">Built With</a></li>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#resources">Resources</a></li>
  </ol>
</details>

## Built With

- [Spacy](https://spacy.io/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Installation

<strong>Create virtual environment</strong>

<h4>Install dependencies</h4>
Run the command:
```
~ pip install -r requirements.txt
```
Alternatively, you can download each required package individually:
```
pip install curl-cffi requests pandas pillow spacy
python -m spacy download en_core_web_lg
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

To run the project locally run the command:
```
python scraper.py
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Resources

<ul>
    <li>[Save images from url](https://stackoverflow.com/questions/30229231/python-save-image-from-url)
    <li>[Basic web scrape example](https://oxylabs.io/blog/python-web-scraping)
    <li>[Scrape image from website](https://oxylabs.io/blog/scrape-images-from-website)
    <li>[Get data from server API](https://www.youtube.com/watch?v=ji8F8ppY8bs&t=767s)
    <li>[Spacy usage](https://www.geeksforgeeks.org/python-named-entity-recognition-ner-using-spacy/)
</ul>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- To Do List -->
<!--
- Debug caption split
- image file names saved as name.jpg.png
- manually check images against csv file
-->

