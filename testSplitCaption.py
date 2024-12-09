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
from spacy import displacy
  

def split_caption(winner, caption):

    # looking for these values
    group = None
    photographers = None
    organization = None

    nlp = spacy.load('en_core_web_lg') 
    
    winnerDoc = nlp(winner) 
    winnerTokens = []
    # create an array for winner tokens
    for token in winnerDoc.ents: 
        winnerTokens.append({"text": token.text, "start_char":token.start_char, "end_char":token.end_char, "label":token.label_}) 
    
    captionAllDoc =  nlp(caption)
    captionAllTokens = []
    # create an array for caption tokens
    for token in captionAllDoc.ents: 
        captionAllTokens.append({"text": token.text, "start_char":token.start_char, "end_char":token.end_char, "label":token.label_}) 

    # check if there are parentheses in caption, if there are save into a string
    parenthesesString = ""
    captionEndDoc =  nlp(parenthesesString)
    captionEndTokens = []
    # create an array for caption tokens
    for token in captionEndDoc.ents: 
        captionEndTokens.append({"text": token.text, "start_char":token.start_char, "end_char":token.end_char, "label":token.label_}) 

    print(winnerTokens)
    print(captionAllTokens)

    # look for names in winner
    photographers = next((ele['text'] for ele in winnerTokens if ele['label'] == "PERSON"), None)

    #there are no names in winner
    if (photographers == None | photographer.length > 1):
        # must be a group name
        group = winner
        # is there "of" in the title? then organization name is after
        if ("of" *is in* winner):
            organization = winner[*index of of*:]
        else:
            #look in caption for organization
            organization = next((ele['text'] for ele in captionEndTokens if ele['label'] == "ORG"), None)
        # look for name in caption
        photographer = next((ele['text'] for ele in captionEndTokens if ele['label'] == "PERSON"), None)

    #there is one name in winner
    else (photographers.length == 1):
        # is there "of" in the title? then organization name is after
        if ("of" *is in* winner):
            organization = winner[*index of of*:]
            # then photographer name is in caption ()
            if parenthesesString != None:
                photographer = next((ele['text'] for ele in captionEndTokens if ele['label'] == "PERSON"), None)
        else:
            photographer = winner
            # organization name may be in parentheses
            if parenthesesString != None:
                organization = next((ele['text'] for ele in captionEndTokens if ele['label'] == "ORG"), None)
    return 

    
    

    
    print(winnerTokens)
    print(captionTokens)

    return 

split_caption("Charles Porter IV", "(April 19. 1995, Charles Porter IV distributed by Associated Press)")

