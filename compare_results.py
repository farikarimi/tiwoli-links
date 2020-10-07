import re

with open('results/missing_quote_links_old_approach_04_03.txt', 'r') as file1:
    text1 = file1.read()

with open('results/missing_quote_links_2020-10-07.txt', 'r') as file2:
    text2 = file2.read()

pattern = r'(?<=first 50 characters of quote: ).*'

matches1 = re.findall(pattern, text1)
matches2 = re.findall(pattern, text2)

missing_quotes_wo_fw = []  # 62
missing_quotes_w_fw = []  # 0

for quote in matches2:
    if quote in matches1:
        missing_quotes_wo_fw.append(quote)
    else:
        missing_quotes_w_fw.append(quote)


print(f'\n{len(missing_quotes_wo_fw)} quotes that could not be found by the old script wihtout fuzzywuzzy:\n')
print(missing_quotes_wo_fw)
print(f'\n\n{len(missing_quotes_w_fw)} quotes that could not be found by fuzzywuzzy but were found by the old script:\n')
print(missing_quotes_w_fw)
