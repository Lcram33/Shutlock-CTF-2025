import re

file_path = "message.txt"

# 1. Lecture du fichier
lines = open(file_path, 'r', encoding="utf-8").read().splitlines()

decoded = []
for line in lines:
    # 2. Trailing whitespace (espaces + tabulations) uniquement
    m = re.search(r'([ \t]+)$', line)
    if not m:
        continue
    trail = m.group(1)

    # 3. Suppression de l’indentation
    trail = trail.lstrip(' ')          # retire 2‑5 espaces de début

    # 4. Conversion espace/tab en bits
    bits = ''.join('1' if c == '\t' else '0' for c in trail)

    if len(bits) == 7:                 # caractère complet
        decoded.append(chr(int(bits, 2)))

# 5. Résultat
print(''.join(decoded))
