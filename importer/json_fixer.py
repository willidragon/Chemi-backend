# import pandas as pd

# df = pd.read_json('/Users/willidragon/Downloads/fixed_1928_reverted.json',lines=True)

# '/Users/willidragon/Downloads/fixed_1928_reverted.json'

import json
from pathlib import Path

def fix_and_read_json(path):
    txt = Path(path).read_text()
    flag = False
    new_txt = ""
    for c in txt:
        new_c = c
        if c == '\'' and not flag:
            new_c = '"'
        if c == '"' and not flag:
            flag = True
        elif c == '"' and flag:
            flag = False
        new_txt += new_c

    # txt = str(txt).replace("'", '"')
    new_txt = str(new_txt).replace("None", '"None"')
    data = json.loads(new_txt)
    return data
