from typing import List, Tuple

def extract_txt_text(txt_path: str) -> List[Tuple[int, str]]:
    """
    Reads a plain text file and returns line-wise chunks.
    """
    results = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            text = line.strip()
            if text:
                results.append((i + 1, text))
    return results
