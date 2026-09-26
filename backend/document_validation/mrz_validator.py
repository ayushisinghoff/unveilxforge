import re


MRZ_WEIGHTS = [7, 3, 1]


def calculate_check_digit(value: str) -> str:

    total = 0

    for index, char in enumerate(value):

        if char.isdigit():
            number = int(char)

        elif char == "<":
            number = 0

        elif "A" <= char <= "Z":
            number = ord(char) - ord("A") + 10

        else:
            number = 0

        total += number * MRZ_WEIGHTS[index % 3]

    return str(total % 10)


def check_digit_valid(value: str, digit: str) -> bool:

    if not digit.isdigit():
        return False

    return calculate_check_digit(value) == digit


def find_mrz_lines(text: str):

    lines = [
        line.strip().upper()
        for line in text.splitlines()
    ]

    mrz_lines = []

    for line in lines:

        clean = re.sub(
            r"[^A-Z0-9<]",
            "",
            line
        )

        if len(clean) >= 40:
            mrz_lines.append(clean)

    return mrz_lines[-2:]


def validate_passport_mrz(text: str) -> dict:

    try:

        lines = find_mrz_lines(text)

        if len(lines) != 2:

            return {
                "status": "REVIEW",
                "detected": False,
                "reason": "Two MRZ lines were not detected."
            }

        line1 = lines[0]
        line2 = lines[1]

        # Passport MRZ normally has 44 characters per line
        line1 = line1.ljust(44, "<")[:44]
        line2 = line2.ljust(44, "<")[:44]

        checks = {}

        # Passport number
        passport_number = line2[0:9]
        passport_digit = line2[9]

        checks["passport_number_check_digit"] = (
            check_digit_valid(
                passport_number,
                passport_digit
            )
        )

        # Date of birth
        dob = line2[13:19]
        dob_digit = line2[19]

        checks["date_of_birth_check_digit"] = (
            check_digit_valid(
                dob,
                dob_digit
            )
        )

        # Expiry
        expiry = line2[21:27]
        expiry_digit = line2[27]

        checks["expiry_check_digit"] = (
            check_digit_valid(
                expiry,
                expiry_digit
            )
        )

        # Personal number
        personal_number = line2[28:42]
        personal_digit = line2[42]

        if personal_digit.isdigit():

            checks["personal_number_check_digit"] = (
                check_digit_valid(
                    personal_number,
                    personal_digit
                )
            )

        # Overall
        failed = [
            key
            for key, value in checks.items()
            if value is False
        ]

        status = (
            "PASS"
            if not failed
            else "REVIEW"
        )

        return {

            "status": status,

            "detected": True,

            "mrz_lines": [
                line1,
                line2
            ],

            "passport_number": passport_number.replace(
                "<",
                ""
            ),

            "date_of_birth_raw": dob,

            "expiry_raw": expiry,

            "nationality": line2[10:13],

            "sex": line2[20],

            "checks": checks,

            "failed_checks": failed,

            "note": (
                "MRZ check-digit validation is a "
                "format/integrity check and does not "
                "prove passport authenticity."
            )
        }

    except Exception as e:

        return {
            "status": "FAIL",
            "detected": False,
            "reason": str(e)
        }