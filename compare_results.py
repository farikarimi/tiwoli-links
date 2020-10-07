import re

with open('results/missing_quote_links_old_approach_04_03.txt', 'r') as file1:
    text1 = file1.read()

with open('results/missing_quote_links_02_06.txt', 'r') as file2:
    text2 = file2.read()

pattern = r'(?<=first 50 characters of quote: ).*'

matches1 = re.findall(pattern, text1)
matches2 = re.findall(pattern, text2)

really_missing_quotes = []  # 62
problem_cases = []  # 66

for quote in matches2:
    if quote in matches1:
        really_missing_quotes.append(quote)
    else:
        problem_cases.append(quote)


print(f'\n{len(really_missing_quotes)} quotes that don\'t exist on projekt-gutenberg.org:\n')
print(really_missing_quotes)
print(f'\n\n{len(problem_cases)} quotes that actually exist on projekt-gutenberg.org but were not found by fuzzywuzzy:\n')
print(problem_cases)
