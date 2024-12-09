"""
- to get photographer, group, organization name
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

    Spot News Photography,1996,6826,Charles Porter IV,porter21996web.jpg,"(April 19. 1995, Charles Porter IV distributed by Associated Press)"
"""

import spacy 
import re
  
nlp = spacy.load('en_core_web_lg') 

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


print(split_caption("Photography Staff of Associated Press", "A Venezuelan migrant stands covered in a wrap while texting, on the banks of the Rio Grande in Matamoros, Mexico, Saturday, May 13, 2023. (AP Photo/Fernando Llano)"))

