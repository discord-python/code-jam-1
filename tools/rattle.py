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
      g - shortest string
      c - counter used to get similarity
      l - length used to supplement similarity
      length_diff_multiplier - multiplier for extra characters
      mp_count - multiplier for the multiplier, increases on every extra space
      s - string used as length-matched word
      o - string used as *not* `o` (is longer)
    '''
    for w in wordset:
        g = get_shortest(w, word)
        c = 0
        length_diff_multiplier = 1.08  # multiplies any characters past the shortest max index incrementally
        mp_count = 1
        l = len(g)
        s = ''
        if g == word:
            s = match_length(word, w)
            o = w
        else:
            s = match_length(w, word)
            o = word

        for i, char in enumerate(o):
            if char != s[i]:
                if char == '~':
                    c += mp_count * length_diff_multiplier
                    mp_count += 1
                else:
                    c += 1

        avg = c / len(s)
        avg = 1.0  - avg
        if avg >= threshold:
            yield avg, w
        else:
            continue
