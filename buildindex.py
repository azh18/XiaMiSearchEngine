# -*- coding:utf-8 -*-

# input = [file1, file2, ...]
# res = {filename: [world1, word2]}

import re
import math
import json



def isChinese(str):
    if re.match('[ \u4e00 -\u9fa5]+', str) != None:
        return True
    else:
        return False


def isEnglish(uchar):
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False


class BuildIndex:


    def __init__(self, files):
        self.tf = {}
        self.df = {}
        self.idf = {}

        self.singers = []
        self.albums = []
        self.songs = []
        self.singersSize = 0
        self.albumsSize = 0
        self.songsSize = 0
        self.songIDTable = {}
        self.albumIDTable = {}
        self.singerIDTable = {}
        self.singerIndex = {}
        self.albumIndex = {}
        self.songIndex = {}

        self.filenames = files
        self.file_to_terms = self.process_files()
        # self.regdex = self.regIndex()
        # self.totalIndex = self.execute()
        # self.vectors = self.vectorize()
        # self.mags = self.magnitudes(self.filenames)



    def process_files(self):
        file_to_terms = {}


        singerIndex = {}
        singerFileName = self.filenames[0]
        cntSinger = 0
        for line in open(singerFileName, 'r', encoding='utf-8'):
            singerItem = json.loads(line)
            # process singer
            singerID = singerItem["artistID"]
            self.singerIDTable[singerID] = cntSinger

            singerItem["albumsIdx"] = []
            singerItem["songsIdx"] = []
            self.singers.append(singerItem)
            singerName = singerItem['artistName'][0]
            if isChinese(singerName[0]):
                for char in singerName:
                    if char in singerIndex.keys():
                        singerIndex[char].append(cntSinger)
                    else:
                        singerIndex[char] = [cntSinger]
                cntSinger += 1
            elif isEnglish(singerName[0]):
                pattern = re.compile('[\W_]+')
                terms = pattern.sub(' ', singerName.lower())
                for term in terms:
                    if term in singerIndex.keys():
                        singerIndex[term].append(cntSinger)
                    else:
                        singerIndex[term] = [cntSinger]
                cntSinger += 1
        self.singersSize = cntSinger

        albumIndex = {}
        albumFileName = self.filenames[1]
        cntAlbum = 0
        for line in open(albumFileName, 'r', encoding='utf-8'):
            albumItem = json.loads(line)
            albumBelongsToSingerID = albumItem["artistID"]
            if albumBelongsToSingerID in self.singerIDTable.keys():
                albumItem["singerIdx"] = self.singerIDTable[albumBelongsToSingerID]
                print(self.singers[albumItem["singerIdx"]])
                self.singers[albumItem["singerIdx"]]["albumsIdx"].append(cntAlbum)
            # process songs
            albumItem["songsIdx"] = []
            # process album
            albumID = albumItem["albumID"]
            self.albumIDTable[albumID] = cntAlbum

            self.albums.append(albumItem)
            albumName = albumItem['albumName']

            if isChinese(albumName[0]):
                for char in albumName:
                    if char in albumIndex.keys():
                        albumIndex[char].append(cntAlbum)
                    else:
                        albumIndex[char] = [cntAlbum]
                cntAlbum += 1
            elif isEnglish(albumName[0]):
                pattern = re.compile('[\W_]+')
                terms = pattern.sub(' ', albumName.lower())
                for term in terms:
                    if term in albumIndex.keys():
                        albumIndex[term].append(cntAlbum)
                    else:
                        albumIndex[term] = [cntAlbum]
                cntAlbum += 1
        self.albumsSize = cntAlbum

        songIndex = {}
        songFileName = self.filenames[2]
        cntSong = 0
        for line in open(songFileName, 'r', encoding='utf-8'):
            songItem = json.loads(line)
            songBelongToAlbumID = songItem["songAlbumID"]
            if songBelongToAlbumID in self.albumIDTable.keys():
                songItem["albumIdx"] = self.albumIDTable[songBelongToAlbumID]
                self.albums[songItem["albumIdx"]]["songsIdx"].append(cntSong)
            songBelongToSingerID = songItem["songSingerID"][0]
            if songBelongToSingerID in self.singerIDTable.keys():
                songItem["singerIdx"] = self.singerIDTable[songBelongToSingerID]
                self.singers[songItem["singerIdx"]]["songsIdx"].append(cntSong)

            self.songs.append(songItem)
            songName = songItem['songName']
            songID = songItem['songID']
            self.songIDTable[songID] = cntSong
            if isChinese(songName[0]):
                for char in songName:
                    if char in songIndex.keys():
                        songIndex[char].append(cntSong)
                    else:
                        songIndex[char] = [cntSong]
                cntSong += 1
            elif isEnglish(songName[0]):
                pattern = re.compile('[\W_]+')
                terms = pattern.sub(' ', songName.lower())
                for term in terms:
                    if term in songIndex.keys():
                        songIndex[term].append(cntSong)
                    else:
                        songIndex[term] = [cntSong]
                cntSong += 1
        self.songsSize = cntSong
        self.singerIndex = singerIndex
        self.albumIndex = albumIndex
        self.songIndex = songIndex
        ccc =4
        ccc =5











        #
        # for file in self.filenames:
        #     # stopwords = open('stopwords.txt').read().close()
        #     pattern = re.compile('[\W_]+')
        #     file_to_terms[file] = open(file, 'r').read().lower();
        #     file_to_terms[file] = pattern.sub(' ', file_to_terms[file])
        #     re.sub(r'[\W_]+', '', file_to_terms[file])
        #     file_to_terms[file] = file_to_terms[file].split()
        # # file_to_terms[file] = [w for w in file_to_terms[file] if w not in stopwords]
        # # file_to_terms[file] = [stemmer.stem_word(w) for w in file_to_terms[file]]
        # return file_to_terms

if __name__ == "__main__":
    index = BuildIndex(["artistJ.json", "albumJ.json", "songJ.json"])


    # # input = [word1, word2, ...]
    # # output = {word1: [pos1, pos2], word2: [pos2, pos434], ...}
    # def index_one_file(self, termlist):
    #     fileIndex = {}
    #     for index, word in enumerate(termlist):
    #         if word in fileIndex.keys():
    #             fileIndex[word].append(index)
    #         else:
    #             fileIndex[word] = [index]
    #     return fileIndex
    #
    # # input = {filename: [word1, word2, ...], ...}
    # # res = {filename: {word: [pos1, pos2, ...]}, ...}
    # def make_indices(self, termlists):
    #     total = {}
    #     for filename in termlists.keys():
    #         total[filename] = self.index_one_file(termlists[filename])
    #     return total
    #
    # # input = {filename: {word: [pos1, pos2, ...], ... }}
    # # res = {word: {filename: [pos1, pos2]}, ...}, ...}
    # def fullIndex(self):
    #     total_index = {}
    #     indie_indices = self.regdex
    #     for filename in indie_indices.keys():
    #         self.tf[filename] = {}
    #         for word in indie_indices[filename].keys():
    #             self.tf[filename][word] = len(indie_indices[filename][word])
    #             if word in self.df.keys():
    #                 self.df[word] += 1
    #             else:
    #                 self.df[word] = 1
    #             if word in total_index.keys():
    #                 if filename in total_index[word].keys():
    #                     total_index[word][filename].append(indie_indices[filename][word][:])
    #                 else:
    #                     total_index[word][filename] = indie_indices[filename][word]
    #             else:
    #                 total_index[word] = {filename: indie_indices[filename][word]}
    #     return total_index
    #
    # def vectorize(self):
    #     vectors = {}
    #     for filename in self.filenames:
    #         vectors[filename] = [len(self.regdex[filename][word]) for word in self.regdex[filename].keys()]
    #     return vectors
    #
    # def document_frequency(self, term):
    #     if term in self.totalIndex.keys():
    #         return len(self.totalIndex[term].keys())
    #     else:
    #         return 0
    #
    # def collection_size(self):
    #     return len(self.filenames)
    #
    # def magnitudes(self, documents):
    #     mags = {}
    #     for document in documents:
    #         mags[document] = pow(sum(map(lambda x: x ** 2, self.vectors[document])), .5)
    #     return mags
    #
    # def term_frequency(self, term, document):
    #     return self.tf[document][term] / self.mags[document] if term in self.tf[document].keys() else 0
    #
    # def populateScores(self):  # pretty sure that this is wrong and makes little sense.
    #     for filename in self.filenames:
    #         for term in self.getUniques():
    #             self.tf[filename][term] = self.term_frequency(term, filename)
    #             if term in self.df.keys():
    #                 self.idf[term] = self.idf_func(self.collection_size(), self.df[term])
    #             else:
    #                 self.idf[term] = 0
    #     return self.df, self.tf, self.idf
    #
    # def idf_func(self, N, N_t):
    #     if N_t != 0:
    #         return math.log(N / N_t)
    #     else:
    #         return 0
    #
    # def generateScore(self, term, document):
    #     return self.tf[document][term] * self.idf[term]
    #
    # def execute(self):
    #     return self.fullIndex()
    #
    # def regIndex(self):
    #     return self.make_indices(self.file_to_terms)
    #
    # def getUniques(self):
    #     return self.totalIndex.keys()
