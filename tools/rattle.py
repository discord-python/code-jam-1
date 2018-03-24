# rattle - easy word similarity detection
def check_word(word: str, wordset: list, threshold:float=0.0):
    '''Checks a word for its similarity to a list of words.
    
    :param word: A word to compare to a list of words.
    :param wordset: An iterable value that `word` will be compared to.
    :param threshold: Optional, only yields similarity values and words that are above the given threshold (1.0 is 100% similarity, 0.45 is 45% similarity, etc.)
    :yield: A similarity value and the word corresponding with it.'''
    def get_shortest(x, y):
        '''Gets the shortest string between x and y.
        
        If both strings are of equal length, x will be returned. (This does not matter in the wrapping function)
        
        :param x: A string.
        :param y: Another string.
        :return: The string that is shorter than the other.'''
        return x if len(x) < len(y) else y

    def match_length(word, otherword):
        '''Append characters to the end of word to meet the length of otherword.
        
        :param word: A shorter word.
        :param otherword: A longer word.
        :return: The shorter word but with extra characters to meet the length of the longer word.'''
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
    for w in wordset:  # check against every word
        shortest = get_shortest(w, word)  # get the shortest word
        count = 0  # prepare the similarity counter
        length_diff_multiplier = 1.08  # set the length difference multiplier
        mp_count = 1  # set the current lendiff count
        shorter = ''  # prepare a variable for readability
        longer = ''  # prepare another variable for readability
        if shortest == word:  # if the shortest word is the given word...
            shorter = match_length(word, w)  # lengthen the given word to match the longer one to avoid IndexErrors
            longer = w  # set the longer word to the cycled word
        else:  # if the shortest word is the cycled word...
            shorter = match_length(w, word)  # length the cycled word to match ''[ditto]
            longer = word  # set longer word to the given word

        for i, char in enumerate(longer):  # for each character and index in the longer word...
            if char != shorter[i]:  # if the characters aren't the same
                if char == '~':  # if the character is an extra space
                    count += mp_count * length_diff_multiplier  # increase the count by the current multiplier
                    mp_count += 1  # increase the "multiplier multiplier" by one
                else:  # if it's just a character difference
                    count += 1  # increase the count by one

        sim = 1.0 - (count / len(shorter))  # get the similarity
        if sim >= threshold:  # if the similarity is above the threshold...
            yield avg, w  # yield the similarity and the cycled word
        else:  # otherwise...
            continue  # continue on with your life
