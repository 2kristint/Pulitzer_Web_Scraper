from curl_cffi import requests as cureq
import json
import time
import hashlib, io, requests, pandas as pd
from PIL import Image
from pathlib import Path

def main():
    #start new session
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.pulitzer.org/",
    }
    session = cureq.Session()
    session.headers.update(headers)
    try:
        #get a list of winner id values
        resp = session.get(
            "https://www.pulitzer.org/cache/api/1/winners/cat/217/raw.json",
            impersonate="chrome"
        )
        print(resp.status_code)
        #headers for debugging
        print("\nResponse Headers:")
        for key, value in resp.headers.items():
            print(f"{key}: {value}")
        winnersList = resp.json()
        nid_values = [entry["nid"] for entry in winnersList if "nid" in entry]
        print(nid_values)

        #go to each winner webpage and grab images and captions

        results = []

        for item in nid_values[:5]:
            resp = session.get(
                f"https://www.pulitzer.org/cache/api/1/node/{item}/raw.json",
                impersonate="chrome"
            )

            resp.raise_for_status()
            winnerData = resp.json()

            #create json dump of webpage
            # with open(f'{item}_data.json', 'w', encoding='utf-8') as f:
            #     json.dump(winnerData, f, ensure_ascii=False, indent=4)

            imageSections = winnerData["field_regular_image_slider"]["und"]

            for section in imageSections:
                item = section["item"]
                image = item["field_slider_image"]["und"][0]["uri"]
                caption = item["field_image_caption"]["und"][0]["safe_value"]

                if image or caption:
                    results.append({"image_url": image or "", "caption": caption or ""})

            time.sleep(10)

        #save images

        df = pd.DataFrame(results)
        df.to_csv('imagesNcaptions.csv', index=False, encoding='utf-8')

        print("data saved to a CSV file")

        # Get the directory where scrapper.py is located
        current_dir = Path(__file__).parent
        #setup directory for images
        output_dir = current_dir / "images1"
        output_dir.mkdir(parents=True, exist_ok=True)

        for result in results:
            try:
                image_content = requests.get(f"https://www.pulitzer.org/cms/sites/default/files/styles/image_slider/public/{result["image_url"][8:]}").content
                image_file = io.BytesIO(image_content)
                image = Image.open(image_file).convert("RGB")
                file_path = output_dir / (hashlib.sha1(image_content).hexdigest()[:10] + ".png")
                image.save(file_path, "PNG", quality=80)
            except:
                print(f"This image was not able to be saved {result["image_url"]}")

        print(f"'images1' folder created at: {output_dir}")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occured: {e}")

    finally:
        session.close()  # Ensure the session is closed
    return

# source of images: https://www.pulitzer.org/cms/sites/default/files/styles/image_slider/public/ap_migration_001_0.jpeg

main()
