import pandas as pd

df = pd.ExcelFile (r'/Users/willidragon/Downloads/110-short.xlsx')

tab1 = pd.read_excel(df, 'TToxChemiOperation');
tab2 = pd.read_excel(df, 'TToxChemiRestAmount');

print(tab1)
print(tab2)