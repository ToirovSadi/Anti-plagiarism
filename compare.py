import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='pair of file_names(path) to compare')
parser.add_argument('output_file', help='file to write result of the program')

ACCEPT_COEFF = 0.3
args = parser.parse_args()
pairs_to_compare = []

# let's go through the pair files from input_file
with open(args.input_file, 'r') as f:
    for file in f.readlines():
        file1 = file.split(' ')[0]
        file2 = file.split(' ')[1]
        if file2.endswith('\n'):
            file2 = file2[:-1]  # remove '\n' at the end of the line
        pairs_to_compare.append((file1, file2))


def levenshtein(s, t):
    rows = len(s) + 1
    cols = len(t) + 1
    dist = [[0 for _ in range(cols)] for _ in range(rows)]
    for i in range(1, rows):
        dist[i][0] = i
    for i in range(1, cols):
        dist[0][i] = i
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = 1
            dist[row][col] = min(dist[row-1][col] + 1,      # deletion
                                 dist[row][col-1] + 1,      # insertion
                                 dist[row-1][col-1]+cost)   # substitution
    return dist[row][col]


junk_char = ['\n', ':', ',']
alf = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# None if word should not be considered anywhere
def clean_word(word):
    if sum([c in alf for c in word]) <= 1:
        return None
    for c in junk_char:
        while word.endswith(c):
            word = word[:-1]
        while word.startswith(c):
            word = word[1:]
    while word.endswith('(') or word.endswith('['):
        word = word[:-1]
    while word.startswith(')') or word.startswith(']'):
        word = word[1:]
    while ((word.startswith('(') and word.count(')') == 0)
           or (word.startswith('[') and word.count(']') == 0)):
        word = word[1:]
    while ((word.endswith(')') and word.count('(') == 0)
           or (word.endswith(']') and word.count('[') == 0)):
        word = word[:-1]
    if len(word) <= 1:
        return None
    return word.lower()


def read_file(filename):
    file_content = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            words = line.split(' ')
            for word in words:
                word = clean_word(word)
                if word is not None:
                    file_content.append(word)
    return file_content


def accept_str(line1, line2):
    diff = levenshtein(line1, line2)
    length = max(len(line1), len(line2))
    if diff >= length:
        return False
    return round(diff/length, 1) <= ACCEPT_COEFF


def compare(file1, file2):
    s1 = set(file1)
    s2 = set(file2)
    total_words = len(s1.union(s2))
    intersection_words = 0

    for word1 in s1:
        accept = False
        for word2 in s2:
            if accept_str(word1, word2):
                accept = True
                break
        intersection_words += accept

    return intersection_words / total_words


scores = []
for pair in pairs_to_compare:
    file1_content = read_file(pair[0])
    file2_content = read_file(pair[1])
    scores.append(compare(file1_content, file2_content))

with open(args.output_file, 'w') as f:
    for score in scores:
        f.write(str(score)+'\n')
