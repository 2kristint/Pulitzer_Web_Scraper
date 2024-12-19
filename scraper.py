from curl_cffi import requests as cureq
import json
import time
import io, requests, pandas as pd
from PIL import Image
from pathlib import Path
import re
from tqdm import tqdm
import spacy
import random

# Load spaCy NLP model
nlp = spacy.load('en_core_web_sm')

# Set up directory for images
current_dir = Path(__file__).parent
output_dir = current_dir / "images"
output_dir.mkdir(parents=True, exist_ok=True)

# Get global JSON. Global JSON is a dictionary in which we can translate the tid values on specific winner webpages to categories and years. 
# For example, the object with the tid "274" is linked to the category, "Spot News Photography".
def get_global_json(session):
    try:
        resp = session.get(
            "https://www.pulitzer.org/cache/api/1/global.json",
            impersonate="chrome",
            timeout = 10
        )
        globalVocab = resp.json()
        with open(f'data/globalVocab.json', 'w', encoding='utf-8') as f:
            json.dump(globalVocab, f, ensure_ascii=False, indent=4)
    except:
        print(f"Unable to get global JSON. Please try running the code again. Response code {resp.status_code}")
    return globalVocab

# Translate tid to name. Searches global JSON for the tid, in order to find the name associated with it.
def get_tid_name(globalVocab, search_tid):
    vocabList = globalVocab["vocabularies"]
    name = next((ele['name'] for ele in vocabList if ele['tid'] == search_tid), None)
    if (name == None):
        print(f"{search_tid} unable to be found")
    return name

# Get list of winner ids (nid) from a category
def get_category_nids(session, tid_category, start, end):
    try:
        resp = session.get(
            f"https://www.pulitzer.org/cache/api/1/winners/cat/{tid_category}/raw.json",
            impersonate="chrome",
            timeout = 10
        )
        winnersList = resp.json()
        all_nid_values = [entry["nid"] for entry in winnersList if "nid" in entry]
        nid_values = all_nid_values[start:end]
        # Pulitzer's robots.txt has crawl-delay: 10
        time.sleep(10)
    except Exception as e:
        print(f"Unable to get nid_values for {tid_category} Error: {e}")
    return nid_values

# Helper method for spaCy language processing. 
# Extracts tokens (recognized words/phrases) from text using spaCy's NLP model. 
def extract_tokens(text):
    if not text:
        return []
    try:
        doc = nlp(text)
        return [{"text": token.text, "start_char": token.start_char, "end_char": token.end_char, "label": token.label_} for token in doc.ents]
    except Exception as e:
        print(f"Error processing text with spaCy: {e}")
        return []
    
# Look for photographer's or group's name, organization, and locations from the title and caption.

# Extract text from parentheses of caption
def extract_parentheses_text(caption):
    match = re.search(r'\(([^)]+)\)', caption)
    return match.group(1) if match else ""

def split_caption(winner, caption):
    group = None
    photographers = None
    organization = None
    locations = None

    # Caption may have formating that intrudes in spaCy analysis.
    # For example, text formatted like AP Photo/Fernando LLano is read as one token and photographer is not able to be identified.
    preprocessedCaption = re.sub(r'[/]', ', ', caption)
    
    # Extract all tokens
    winnerTokens = extract_tokens(winner)
    captionTokens = extract_tokens(preprocessedCaption)
    parenthesesText = extract_parentheses_text(preprocessedCaption)
    parenthesesTokens = extract_tokens(parenthesesText)

    # Look for names in the title
    photographers = [ele['text'] for ele in winnerTokens if ele['label'] == "PERSON"]

    # If there are no names in winner
    if len(photographers) != 1:
        # Title must be a group name
        group = winner
        # Is there "of" in the title? Then organization name is after
        if "of" in winner:
            organization = winner.split("of", 1)[1].strip()
        else:
            # Look in parentheses for organization
            organization = next((ele['text'] for ele in parenthesesTokens if ele['label'] == "ORG"), None)
        # Look for name in caption
        photographer = next((ele['text'] for ele in parenthesesTokens if ele['label'] == "PERSON"), None)
    #If there is one name in winner
    else:
        photographer = photographers[0]
        # Is there "of" in the title? Then organization name is after
        if "of" in winner:
            organization = winner.split("of", 1)[1].strip()
            # Then photographer name is in caption ()
        elif parenthesesText:
                organization = next((ele['text'] for ele in parenthesesTokens if ele['label'] == "ORG"), None)

     # Extract locations from caption tokens
    locations = list({ele['text'] for ele in captionTokens if ele['label'] in ("GPE", "LOC")}) 
    return group, organization, photographer, locations

# Get data from winner's JSON object
def get_winner_data(globalVocab, session, nid_list):
    for nid in tqdm(nid_list):
        try:
            resp = session.get(
                f"https://www.pulitzer.org/cache/api/1/node/{nid}/raw.json",
                impersonate="chrome",
                timeout = 10
            )

            resp.raise_for_status()
            winnerData = resp.json()

            winners  = winnerData["title"]
            year = get_tid_name(globalVocab, winnerData["field_year"]["und"][0]["tid"])
            fieldCategory = get_tid_name(globalVocab, winnerData["field_category"]["und"][0]["tid"])
            imageSections = winnerData["field_regular_image_slider"]["und"]

            imageData = []

            for section in imageSections:
                item = section["item"]
                # Some sections don't have images
                try:
                    image = item["field_slider_image"]["und"][0]["uri"][9:]
                except:
                    continue
                # Some images have no captions
                try:
                    caption = item["field_image_caption"]["und"][0]["safe_value"]
                except:
                    caption = "N/A"

                if image:
                    # Look for photographer's or group's name, organization, and locations from the title and caption.
                    if caption:
                        try:
                            group, organization, photographer, locations = split_caption(winners, caption)
                        except:
                            print("Error occured in split caption")
                    
                    # Save image
                    sanitized_filename = "".join(c if c.isalnum() or c in (' ', '.', '_', '-') else '_' for c in image) + ".png"
                    file_path = output_dir / sanitized_filename
                    with Image.open(io.BytesIO(requests.get(f"https://www.pulitzer.org/cms/sites/default/files/styles/image_slider/public/{image}").content)) as img:
                        img.save(file_path, "PNG", quality=80)
                    
                    # Add image data to an array
                    imageData.append({"Image_URL": image, 
                                    "Category": fieldCategory, 
                                    "Year": year, 
                                    "Group": group or "", 
                                    "Photographer": photographer or "", 
                                    "Organization": organization or "", 
                                    "Locations": locations or "", 
                                    "Caption": caption or ""})
                    
            # Write image data to csv file
            df = pd.DataFrame(imageData)
            df.to_csv('data/winner_data.csv', mode='a', index=False, encoding='utf-8', header=not Path('data/winner_data.csv').exists())
            imageData.clear()

            # Pulitzer's robots.txt has crawl-delay: 10
            time.sleep(random.uniform(9, 11))
            
        except Exception as e:
            print(f"Error occurred with getting data for nid: {nid}, {e}. This error is mostly likely because there is no images on the page.")
    return 

# Main function: Start session to get global.JSON, get nid values, and get winner data. 
def main():

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.pulitzer.org/",
    }

    with cureq.Session() as session:
        session.headers.update(headers)

        # Get global JSON
        globalVocab = get_global_json(session)
        print(f"Able to get global JSON successfully.")

        # Get a list of winner id values (nid)
        feature_photography_nid_list = get_category_nids(session, 217, 0, 30)
        print(f"List of winner ids for Feature Photography: {feature_photography_nid_list}")
        breaking_news_photography_nid_list = get_category_nids(session, 216, 0, 25)
        print(f"List of winner ids for Breaking News Photography: {breaking_news_photography_nid_list}")
        spot_news_photography_nid_list = get_category_nids(session, 274, 0, 15)
        print(f"List of winner ids for Spot News Photography: {spot_news_photography_nid_list}")

        print("Getting Feature Photography data")
        get_winner_data(globalVocab, session, feature_photography_nid_list)

        print("Getting Breaking News Photography data")
        get_winner_data(globalVocab, session, breaking_news_photography_nid_list)

        print("Getting Spot News Photography data")
        get_winner_data(globalVocab, session, spot_news_photography_nid_list)

        return
    
# Run Main
main()
print("🎉 All tasks completed successfully!")