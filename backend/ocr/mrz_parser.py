import re


def mrz_check_digit(data):
    """
    Calculates the MRZ check digit.
    """

    weights = [7, 3, 1]
    total = 0

    for i, char in enumerate(data):

        if char.isdigit():
            value = int(char)

        elif char.isalpha():
            value = ord(char) - ord("A") + 10

        else:
            value = 0

        total += value * weights[i % 3]

    return str(total % 10)


def clean_mrz_line(line):
    line = line.upper()
    line = line.replace(" ", "")
    line = re.sub(r"[^A-Z0-9<]", "", line)
    return line


def find_mrz_lines(ocr_text):
    """
    Finds likely passport MRZ lines from OCR output.
    """

    mrz_lines = []

    for text in ocr_text:

        line = clean_mrz_line(text)

        if line.startswith("P<") and len(line) >= 20:
            mrz_lines.append(line)

        elif (
            len(line) >= 30
            and "<" in line
            and any(char.isdigit() for char in line)
        ):
            mrz_lines.append(line)

    return mrz_lines


def convert_mrz_date(date):
    """
    Converts YYMMDD → YYYY-MM-DD.
    """

    if len(date) != 6 or not date.isdigit():
        return None

    year = int(date[0:2])
    month = int(date[2:4])
    day = int(date[4:6])

    if year >= 50:
        year += 1900
    else:
        year += 2000

    return f"{year:04d}-{month:02d}-{day:02d}"


def parse_mrz(lines):

    result = {
        "valid": False,
        "document_type": None,
        "issuing_country": None,
        "surname": None,
        "given_names": None,
        "passport_number": None,
        "nationality": None,
        "date_of_birth": None,
        "sex": None,
        "date_of_expiry": None,
        "raw_mrz": lines
    }

    if len(lines) < 2:
        return result

    line1 = lines[0]
    line2 = lines[1]

    # Make both lines 44 characters
    line1 = line1[:44].ljust(44, "<")
    line2 = line2[:44].ljust(44, "<")

    # -----------------------------
    # MRZ LINE 1
    # -----------------------------

    result["document_type"] = line1[0]

    result["issuing_country"] = line1[2:5]

    name_section = line1[5:]

    name_parts = name_section.split("<<")

    result["surname"] = (
        name_parts[0]
        .replace("<", " ")
        .strip()
    )

    if len(name_parts) > 1:

        result["given_names"] = (
            name_parts[1]
            .replace("<", " ")
            .strip()
        )

    # -----------------------------
    # MRZ LINE 2
    # -----------------------------

    result["passport_number"] = (
        line2[0:9]
        .replace("<", "")
    )

    passport_number_raw = line2[0:9]
    passport_number_check = line2[9]

    result["passport_number_checksum"] = (
        mrz_check_digit(passport_number_raw)
        == passport_number_check
    )

    result["nationality"] = line2[10:13]

    # Date of birth
    dob = line2[13:19]

    result["date_of_birth"] = convert_mrz_date(dob)

    # Sex
    sex = line2[20]

    if sex != "<":
        result["sex"] = sex

    # Expiry date
    expiry = line2[21:27]

    result["date_of_expiry"] = convert_mrz_date(expiry)

    result["valid"] = True

    return result