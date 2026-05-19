from itertools import count


_barcode_counter = count(1)


def generate_barcode() -> str:
    return f"BC-2026-{next(_barcode_counter):06d}"
