from curl_cffi import requests as cureq
import json
import time
import hashlib, io, requests, pandas as pd
from PIL import Image
from pathlib import Path

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

#get more information from caption and winners

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

            # create json dump of webpage
            with open(f'winner_data.json', 'w', encoding='utf-8') as f:
                json.dump(winnerData, f, ensure_ascii=False, indent=4)
            
            winners  = winnerData["title"]
            print(winners)
            year = get_tid_name(globalVocab, winnerData["field_year"]["und"][0]["tid"])
            print(year)
            fieldCategory = get_tid_name(globalVocab, winnerData["field_category"]["und"][0]["tid"])
            print(fieldCategory)
            imageSections = winnerData["field_regular_image_slider"]["und"]

            for section in imageSections:
                item = section["item"]
                print(item)
                # some sections don't have images
                try:
                    image = item["field_slider_image"]["und"][0]["uri"][9:]
                except:
                    continue
                print(image)
                try:
                    caption = item["field_image_caption"]["und"][0]["safe_value"]
                except:
                    caption = "N/A"
                print(caption)

                if image or caption:
                    results.append({"Category": fieldCategory, "Year": year, "nid" : nid, "Winners": winners or "", "Image_URL": image or "", "Caption": caption or ""})
                    print(image)
                    print(caption)
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

        #create csv file with image and caption info
        results = []
        #get data from each winner's page and apend data to results

        get_winner_data(globalVocab, session, [6826], results)

        df = pd.DataFrame(results)
        df.to_csv('data/winner_data.csv', index=False, encoding='utf-8')
        print("data saved to a CSV file")

        #save images
        get_images(results)

        return

# source of images: https://www.pulitzer.org/cms/sites/default/files/styles/image_slider/public/ap_migration_001_0.jpeg

main()
