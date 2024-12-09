# Pulitzer_Web_Scraper
1) download images from page, rename images (pp-001), put in folder
2) create spreadsheet corresponding to image id ^, with information: 
    •	Date Awarded (Year only) X
    •	Photographer Name X
    •	Photographer’s country of origin (if possible)
    •	If Group Award, what group (e.g., Staff of Reuters, Staff of Associated Press) X
    •	Location of where image was taken (city and country or just city). X
    •	News Outlet worked for (if applicable, e.g. Dallas Morning News, Associated Press, etc)
    •	Competition Category (e.g. Spot News, Breaking News, Feature Photography)
    •	Caption


img_file | Competition Category | Date (Year) | Group | Photographer | Organization | caption 


- to get author, group, organization name
    - if unable to locate name in title?
        - group name
        - if "of" in title
            - after "of" is organization
    - if able to locate 1 name in title
        - if there is not an "of"
            - title is photographer name
        - if there is an "of"
            - locate parentheses ()
            - use language to identify name
            - after "of" is organization name
    - if able to locate +1 name in title
        - names are group award
        - after "of" is organization
        - or locate parentheses (/organization name)
- to get location
    - use the API to locate all locations in the caption and save to an array to be sorted manually


GOAL: create python script that produces folder of pictures and csv file

# start at website and go to link
# grab image from page using beautiful soup
# download image on page
# rename image in folder
# grab information associated with image

https://stackoverflow.com/questions/30229231/python-save-image-from-url
https://oxylabs.io/blog/python-web-scraping
https://oxylabs.io/blog/scrape-images-from-website
https://www.geeksforgeeks.org/python-named-entity-recognition-ner-using-spacy/
https://medium.com/ubiai-nlp/fine-tuning-spacy-models-customizing-named-entity-recognition-for-domain-specific-data-3d17c5fc72ae

#use:
    beautifulsoup - webscrape
    pandas - data organization



imports:

pip install curl-cffi requests pandas pillow spacy
python -m spacy download en_core_web_lg


# create virtual environment

