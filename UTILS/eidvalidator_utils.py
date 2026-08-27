import re

class EmiratesIDValidator:

    @staticmethod
    def is_valid_format(eid: str) -> bool:
        """
        Validates Emirates ID basic format:
        784-YYYY-XXXXXXX-X
        """

        if not eid:
            return False

        eid = eid.strip()

        pattern = r"^784-\d{4}-\d{7}-\d{1}$"

        return bool(re.match(pattern, eid))

