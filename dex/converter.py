import re
from pathlib import Path

SRC = Path(__file__).with_name('moves_cleaned.ts')
DST = Path(__file__).with_name('moves_converted.py')

def main():
    text = SRC.read_text(encoding='utf-8')

    # remove block comments /* ... */
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    # remove line comments //...
    text = re.sub(r'//.*', '', text)

    # Quote unquoted object keys (repeatedly until stable)
    key_pattern = re.compile(r'(?P<prefix>[\{,\n])\s*(?P<key>[A-Za-z0-9_\-]+)\s*:')
    prev = None
    while prev != text:
        prev = text
        text = key_pattern.sub(r"\g<prefix>\"\g<key>\":", text)

    # Replace JS booleans/null with Python equivalents
    text = re.sub(r"\btrue\b", "True", text)
    text = re.sub(r"\bfalse\b", "False", text)
    text = re.sub(r"\bnull\b", "None", text)

    # Remove unnecessary backslashes that escape double quotes (from earlier conversions)
    text = text.replace('\\"', '"')

    # Fix trailing commas before closing braces/brackets (optional in Python, but keep them)

    # Ensure the file has a valid assignment to `dex` (keep as-is)

    DST.write_text(text, encoding='utf-8')
    print(f'Wrote {DST}')

if __name__ == "__main__":
    main()
