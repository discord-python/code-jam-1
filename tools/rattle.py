# rattle - easy word similarity detection
def check_word(word, wordset, threshold=0.8):
    def get_shortest(x, y):
        return x if len(x) < len(y) else y

    def match_length(word, otherword):
        h = len(otherword) - len(word)
        word += '~' * h
        return word
    '''
      glossary:
      shortest - shortest string
      count - counter used to get similarity
      length_diff_multiplier - multiplier for extra characters
      mp_count - multiplier for the multiplier, increases on every extra space
      shorter - string used as length-matched word
      longer - string used as *not* `o` (is longer)
    '''
    for w in wordset:
        shortest = get_shortest(w, word)
        count = 0
        length_diff_multiplier = 1.08
        mp_count = 1
        shorter = ''
        if shortest == word:
            shorter = match_length(word, w)
            longer = w
        else:
            shorter = match_length(w, word)
            longer = word

        for i, char in enumerate(longer):
            if char != shorter[i]:
                if char == '~':
                    count += mp_count * length_diff_multiplier
                    mp_count += 1
                else:
                    count += 1

        avg = count / len(shorter)
        avg = 1.0 - avg
        if avg >= threshold:
            yield avg, w
        else:
            continue
