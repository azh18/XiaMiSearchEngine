import buildindex
import re

class Query:
    def __init__(self, filenames):
        self.filenames = filenames
        self.index = buildindex.BuildIndex(self.filenames)

    def freeQuery(self, keywords):
        songsImmidiate = []
        for char in keywords:
            if not len(songsImmidiate):
                songsImmidiate = self.index.songIndex[char]
            else:
                songsImmidiate = list(set(songsImmidiate).intersection(set(self.index.songIndex[char])))
        for item in songsImmidiate:
            print(self.index.songs[item])



if __name__ == "__main__":
    q = Query(["artistJ.json", "albumJ.json", "songJ.json"])
    q.freeQuery("安静")