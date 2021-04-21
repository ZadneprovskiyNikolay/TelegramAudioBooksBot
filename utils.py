import re

def matches(regex: str, input: str):
    print(f'inline message: {input}')
    pattern = re.compile(regex)
    return bool(pattern.search(input))