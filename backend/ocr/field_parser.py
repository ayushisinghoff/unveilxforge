
import re 
 
 
def clean_text(text): 
    return re.sub(r"\s+", " ", text.upper()).strip() 
 
 
def extract_fields(ocr_text): 
 
    fields = { 
        "name": None, 
        "passport_number": None, 
        "nationality": None, 
        "date_of_birth": None, 
        "expiry_date": None, 
        "sex": None 
    } 
 
    text = " ".join(ocr_text) 
    text = clean_text(text) 
 
    # ----------------------------- 
    # PASSPORT NUMBER 
    # ----------------------------- 
 
    passport_match = re.search( 
        r"\b[A-Z]{2,3}\d{6,9}\b", 
        text 
    ) 
 
    if passport_match: 
        fields["passport_number"] = passport_match.group() 
 
    # ----------------------------- 
    # NATIONALITY 
    # ----------------------------- 
 
    nationality_match = re.search( 
        r"\b(AUR|IND|USA|GBR|CAN|AUS|FRA|DEU|JPN)\b", 
        text 
    ) 
 
    if nationality_match: 
        fields["nationality"] = nationality_match.group() 
 
    # ----------------------------- 
    # DATES 
    # ----------------------------- 
 
    dates = re.findall( 
        r"\b\d{2}\s+[A-Z]{3}\s+\d{4}\b", 
        text 
    ) 
 
    if len(dates) >= 2: 
        fields["date_of_birth"] = dates[0] 
        fields["expiry_date"] = dates[-1] 
 
    # ----------------------------- 
    # NUMERIC DOB 
    # ----------------------------- 
 
    numeric_dob = re.search( 
        r"\b\d{2}/\d{2}/\d{4}\b", 
        text 
    ) 
 
    if numeric_dob: 
        fields["date_of_birth"] = numeric_dob.group() 
 
    # ----------------------------- 
    # AADHAAR NUMBER 
    # ----------------------------- 
 
    aadhaar_match = re.search( 
        r"\b\d{4}\s+\d{4}\s+\d{4}\b", 
        text 
    ) 
 
    if aadhaar_match: 
        fields["passport_number"] = ( 
            aadhaar_match.group().replace(" ", "") 
        ) 
 
    # ----------------------------- 
    # SEX 
    # ----------------------------- 
 
    # Only accept M/F when OCR detects 
    # it as a complete separate line. 
 
    for line in ocr_text: 
 
        cleaned_line = line.strip().upper() 
 
        if cleaned_line in ["M", "F"]: 
            fields["sex"] = cleaned_line 
            break 
 
    # ----------------------------- 
    # NAME 
    # ----------------------------- 
 
    # First try to extract name from an Aadhaar-style document. 
 
    for i, line in enumerate(ocr_text): 
 
        cleaned_line = line.strip().upper() 
 
        if cleaned_line == "NAME" and i + 1 < len(ocr_text): 
 
            possible_name = ocr_text[i + 1].strip().upper() 
 
            if possible_name: 
                fields["name"] = possible_name 
                break 
 
    return fields

