import re
# from findGrid import convert


def findWords(file, grid):
    # grid = convert(file)
    nrows, ncols = len(grid), len(grid[0])
    print('------------')
    print('\n'.join(grid))
    print('------------')
    # A dictionary word that could be a solution must use only the grid's
    # letters and have length >= 3. (With a case-insensitive match.)
    alphabet = ''.join(set(''.join(grid)))
    bogglable = re.compile('[' + alphabet + ']{3,}$', re.I).match

    file = open('realWords.txt', 'r')

    words = set(word.rstrip('\n').lower() for word in file if bogglable(word))
    prefixes = set(word[:i] for word in words for i in range(2, len(word)+1))

    def solve():
        for y, row in enumerate(grid):
            for x, letter in enumerate(row):
                for result in extending(letter, ((x, y),)):
                    yield result

    def extending(prefix, path):
        if prefix in words:
            yield (prefix, path)
        for (nx, ny) in neighbors(path[-1]):
            if (nx, ny) not in path:
                prefix1 = prefix + grid[ny][nx]
                if prefix1 in prefixes:
                    for result in extending(prefix1, path + ((nx, ny),)):
                        yield result

    def neighbors(lastPathIndex):
        x = lastPathIndex[0]
        y = lastPathIndex[1]
        for nx in range(max(0, x-1), min(x+2, ncols)):
            for ny in range(max(0, y-1), min(y+2, nrows)):
                yield (nx, ny)

    d = {}
    s = list((word, path) for (word, path) in solve())
    for entry in s:
        if entry[0] not in d:
            d[entry[0]] = [entry[1]]
        else:
            d[entry[0]].append(entry[1])

    words = list(d.keys())
    words.sort(key=lambda x: len(x), reverse=True)

    # for i in range(10):
    #     word = words[i]
    #     print(word, d[word][0][0])

    # if len(words) < 50:
    #     return words[:len(words)]
    # else:
    return words, d


# result = findWords('newApp/2.jpeg')
