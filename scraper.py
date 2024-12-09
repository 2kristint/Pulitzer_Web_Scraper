from curl_cffi import requests as cureq
import json
import time
import io, requests, pandas as pd
from PIL import Image
from pathlib import Path
import spacy 
import re

nlp = spacy.load('en_core_web_lg') 

#** Pulitzer Prizes uses an id system to note prize categories and years for webpages, 
# to translate the id to text and numbers we can recognize we must grab global.json
def get_global_json(session):
    try:
        resp = session.get(
            "https://www.pulitzer.org/cache/api/1/global.json",
            impersonate="chrome"
        )
        print(resp.status_code)
        globalVocab = resp.json()
        #create json dump of webpage
        with open(f'data/globalVocab.json', 'w', encoding='utf-8') as f:
            json.dump(globalVocab, f, ensure_ascii=False, indent=4)
    except:
        print("Unable to get global.json")
    return globalVocab

#Translate tid to name
def get_tid_name(globalVocab, search_tid):
    vocabList = globalVocab["vocabularies"]
    name = next((ele['name'] for ele in vocabList if ele['tid'] == search_tid), None)
    if (name == None):
        print(f"{search_tid} unable to be found")
    return name

def get_category_nids(session, tid_category, start, end):
    try:
        resp = session.get(
            f"https://www.pulitzer.org/cache/api/1/winners/cat/{tid_category}/raw.json",
            impersonate="chrome"
        )
        print(resp.status_code)
        #headers for debugging
        # print("\nResponse Headers:")
        # for key, value in resp.headers.items():
        #     print(f"{key}: {value}")
        winnersList = resp.json()
        all_nid_values = [entry["nid"] for entry in winnersList if "nid" in entry]
        nid_values = all_nid_values[start:end]
        print(nid_values)
    except Exception as e:
        print(f"Unable to get nid_values for {tid_category} Error: {e}")
    return nid_values


def extract_tokens(text):
    """ Extracts tokens from text using spaCy's NLP model. """
    if not text:
        return []
    doc = nlp(text)
    return [{"text": token.text, "start_char": token.start_char, "end_char": token.end_char, "label": token.label_} for token in doc.ents]

def extract_parentheses_text(caption):
    """ Extracts the text inside parentheses from the caption. """
    match = re.search(r'\(([^)]+)\)', caption)
    return match.group(1) if match else ""

def split_caption(winner, caption):

    # looking for these values
    group = None
    photographers = None
    organization = None
    locations = None

    # caption may have formating that intrudes in spacy analysis 
    # (text formatted like AP Photo/Fernando LLano is read as one token and photographer is not able to be identified)
    preprocessedCaption = re.sub(r'[/]', ', ', caption)
    
    # Extract all tokens
    winnerTokens = extract_tokens(winner)
    captionTokens = extract_tokens(preprocessedCaption)
    parenthesesText = extract_parentheses_text(preprocessedCaption)
    parenthesesTokens = extract_tokens(parenthesesText)

    print("Winner Tokens:", winnerTokens)
    print("Caption Tokens:", captionTokens)
    print("Parentheses Tokens:", parenthesesTokens)

    # look for names in winner
    photographers = [ele['text'] for ele in winnerTokens if ele['label'] == "PERSON"]

    #there are no names in winner
    if len(photographers) != 1:
        # must be a group name
        group = winner
        # is there "of" in the title? then organization name is after
        if "of" in winner:
            organization = winner.split("of", 1)[1].strip()
        else:
            #look in parentheses for organization
            organization = next((ele['text'] for ele in parenthesesTokens if ele['label'] == "ORG"), None)
        # look for name in caption
        photographer = next((ele['text'] for ele in parenthesesTokens if ele['label'] == "PERSON"), None)
    #there is one name in winner
    else:
        photographer = photographers[0]
        # is there "of" in the title? then organization name is after
        if "of" in winner:
            organization = winner.split("of", 1)[1].strip()
            # then photographer name is in caption ()
        elif parenthesesText:
                organization = next((ele['text'] for ele in parenthesesTokens if ele['label'] == "ORG"), None)

     # Extract locations from caption tokens
    locations = list({ele['text'] for ele in captionTokens if ele['label'] in ("GPE", "LOC")})  # Use a set to avoid duplicates

    return group, organization, photographer, locations

def get_winner_data(globalVocab, session, nid_list, results):
    for nid in nid_list:
        try:
            resp = session.get(
                f"https://www.pulitzer.org/cache/api/1/node/{nid}/raw.json",
                impersonate="chrome"
            )

            resp.raise_for_status()
            winnerData = resp.json()

            print(f"Saving {nid} data")

            #create json dump of webpage
            # with open(f'{item}_data.json', 'w', encoding='utf-8') as f:
            #     json.dump(winnerData, f, ensure_ascii=False, indent=4)

            winners  = winnerData["title"]
            year = get_tid_name(globalVocab, winnerData["field_year"]["und"][0]["tid"])
            fieldCategory = get_tid_name(globalVocab, winnerData["field_category"]["und"][0]["tid"])
            imageSections = winnerData["field_regular_image_slider"]["und"]

            for section in imageSections:
                item = section["item"]
                # some sections don't have images
                try:
                    image = item["field_slider_image"]["und"][0]["uri"][9:]
                except:
                    continue
                # some images have no captions
                try:
                    caption = item["field_image_caption"]["und"][0]["safe_value"]
                except:
                    caption = "N/A"

                if image:
                    # grab data from caption and compare to winners data
                    group, organization, photographer, locations = split_caption(winners, caption)
                    # add data to csv
                    results.append({"Image_URL": image or "", 
                                    "Category": fieldCategory, 
                                    "Year": year, 
                                    "Group": group or "", 
                                    "Photographer": photographer or "", 
                                    "Organization": organization or "", 
                                    "Locations": locations or "", 
                                    "Caption": caption or ""})
                    # add image to folder
                    
            time.sleep(10)
        except Exception as e:
            print(f"Error occurred with getting data for nid: {nid}, {e}")
    return 

def get_images(results):
    try:
        # Get the directory where scrapper.py is located
        current_dir = Path(__file__).parent
        #setup directory for images
        output_dir = current_dir / "images"
        output_dir.mkdir(parents=True, exist_ok=True)

        for result in results:
            try:
                image_url = result["Image_URL"]
                sanitized_filename = "".join(c if c.isalnum() or c in (' ', '.', '_', '-') else '_' for c in image_url) + ".png"
                image_content = requests.get(f"https://www.pulitzer.org/cms/sites/default/files/styles/image_slider/public/{image_url}").content
                image_file = io.BytesIO(image_content)
                image = Image.open(image_file).convert("RGB")
                file_path = output_dir / sanitized_filename
                image.save(file_path, "PNG", quality=80)
            except:
                print(f"This image was not able to be saved {result["image_url"]}")

        print(f"'images' folder created at: {output_dir}")
    except Exception as e:
        print(f"An error occured: {e}")


def main():
    #start new session
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.pulitzer.org/",
    }

    with cureq.Session() as session:
        session.headers.update(headers)

        #Get global vocabulary
        globalVocab = get_global_json(session)

        #get a list of winner id values (nid)
        feature_photography_nid_list = get_category_nids(session, 217, 0, 30)
        breaking_news_photography_nid_list = get_category_nids(session, 216, 0, 25)
        spot_news_photography_nid_list = get_category_nids(session, 274, 0, 15)


        #create csv file with image and caption info
        results = []
        #get data from each winner's page and apend data to results
        print("Getting Feature Photography data")
        get_winner_data(globalVocab, session, feature_photography_nid_list, results)
        print("Getting Breaking News Photography data")
        get_winner_data(globalVocab, session, breaking_news_photography_nid_list, results)
        print("Getting Spot News Photography data")
        get_winner_data(globalVocab, session, spot_news_photography_nid_list, results)
        df = pd.DataFrame(results)
        df.to_csv('data/winner_data.csv', index=False, encoding='utf-8')
        print("data saved to a CSV file")

        #save images
        get_images(results)

        return

# source of images: https://www.pulitzer.org/cms/sites/default/files/styles/image_slider/public/ap_migration_001_0.jpeg

main()
