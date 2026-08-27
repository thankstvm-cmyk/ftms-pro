import re

MOBILE_CODES = ["050", "052", "054", "055", "056", "058"]

class PhoneValidator:

    # ---------------- CLEAN INPUT ----------------
    @staticmethod
    def clean_number(raw):
        return re.sub(r"[^\d+]", "", raw)

    # ---------------- NORMALIZE ----------------
    @staticmethod
    def normalize_number(raw):
        raw = PhoneValidator.clean_number(raw)

        if raw.startswith("+971"):
            raw = raw[4:]
        elif raw.startswith("971"):
            raw = raw[3:]

        # Case 1: 501234567
        if len(raw) == 9:
            code = "0" + raw[:2]
            number = raw[2:]

        # Case 2: 0501234567
        elif len(raw) == 10:
            code = raw[:3]
            number = raw[3:]

        else:
            return None, None

        return code, number

    # ---------------- VALIDATION ----------------
    @staticmethod
    def validate(code, number):

        # Must be UAE mobile starting with 05
        if not code.startswith("05"):
            return False, "Not a UAE mobile number"

        if code in MOBILE_CODES:
            if number.isdigit() and len(number) == 7:
                return True, "Mobile"
            return False, "Invalid mobile number"

        return False, "Invalid mobile prefix"

    # ---------------- FORMAT ----------------
    @staticmethod
    def to_international(code, number):
        return f"+971{code.lstrip('0')}{number}"

    @staticmethod
    def format_display(code, number):
        code_clean = code.lstrip("0")
        return f"+971 {code_clean} {number[:3]} {number[3:]}"

    # ---------------- MAIN FUNCTION ----------------
    @staticmethod
    def process_uae_number(raw_input):

        code, number = PhoneValidator.normalize_number(raw_input)

        if not code:
            return {
                "valid": False,
                "error": "Invalid format",
                "code": None,
                "number": None,
                "type": None,
                "formatted": None,
                "display": None
            }

        is_valid, phone_type = PhoneValidator.validate(code, number)

        if not is_valid:
            return {
                "valid": False,
                "error": phone_type,
                "code": code,
                "number": number,
                "type": None,
                "formatted": None,
                "display": None
            }

        return {
            "valid": True,
            "error": None,
            "code": code,
            "number": number,
            "type": phone_type,
            "formatted": PhoneValidator.to_international(code, number),
            "display": PhoneValidator.format_display(code, number)
        }