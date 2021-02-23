import json
from findGrid import convert
from boggle import findWords
from google.cloud import storage


def main(fileName):
    grid, data = convert(fileName)
    wordList, wordDict = findWords(fileName, grid)
    # print(wordList)
    jsonData = {'positionData': data,
                "wordList": wordList, "wordDict": wordDict}
    file = open('output.json', 'w')
    json.dump(jsonData, file)
    file.close()


if __name__ == "__main__":
    main('newApp/2.jpeg')
