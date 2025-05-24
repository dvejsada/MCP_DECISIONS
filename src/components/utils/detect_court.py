
def detect_court_type(case_number: str) -> str:
    """Detect which court based on case number format"""
    import re

    # Constitutional Court - contains "ÚS"
    if "ÚS" in case_number:
        return "constitutional"

    # Supreme Court - contains "Cdo" or "Tdo"
    if re.search(r'\b(Cdo|Tdo)\b', case_number):
        return "supreme"

    # Supreme Administrative Court - check for registry identificators
    admin_court_registries = [
        "As", "Ads", "Afs", "Aprk", "Aprn", "Ars", "Azs", "Ao", "Aos",
        "Av", "Komp", "Konf", "Kse", "Kseo", "Kss", "Ksz", "Nk", "Na",
        "Ns", "Nad", "Nao", "Obn", "Pst", "Vol", "Rs", "Nv"
    ]

    for registry in admin_court_registries:
        if re.search(rf'\b{registry}\b', case_number):
            return "supreme_administrative"

    return "unknown"