import json
from collections import defaultdict

def build_positional_index(filename_words, filename_output):
    words_by_length = defaultdict(list)
    
    # Read and group words by their length
    with open(filename_words, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if not word:
                continue
            words_by_length[len(word)].append(word)

    pos_index = {}

    for length, words in words_by_length.items():
        n = len(words)
        # For each letter and each position, store a bitset (as an int)
        letter_pos = {ch: [0] * length for ch in 'abcdefghijklmnopqrstuvwxyz'}

        for i, word in enumerate(words):
            for pos, ch in enumerate(word):
                if ch not in letter_pos:
                    continue
                letter_pos[ch][pos] |= (1 << i)

        pos_index[length] = {
            '_words': words,
            '_letter_pos': letter_pos
        }

    # Convert large integers (bitsets) to hex strings for JSON storage
    for length in pos_index:
        for letter in pos_index[length]['_letter_pos']:
            for pos in range(length):
                bitset_int = pos_index[length]['_letter_pos'][letter][pos]
                pos_index[length]['_letter_pos'][letter][pos] = hex(bitset_int)[2:] or '0'

    with open(filename_output, 'w', encoding='utf-8') as f_out:
        json.dump(pos_index, f_out, indent=2)
    print(f'Positional index saved to {filename_output}')

if __name__ == '__main__':
    build_positional_index('words.txt', 'pos_index.json')
