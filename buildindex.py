# -*- coding:utf-8 -*-

# input = [file1, file2, ...]
# res = {filename: [world1, word2]}

import re
import math
import json

def isChineseLyric(str):
    # if re.match('[ \u4e00 -\u9fa5]+', str) != None:
    cntCh = 0
    cntEng = 0
    for char in str:
        if u'\u4e00' <= char <= u'\u9fff':
            cntCh += 1
        else:
            cntEng += 1
        if cntCh > cntEng + 10:
            return True
    return False

def isChinese(str):
    # if re.match('[ \u4e00 -\u9fa5]+', str) != None:
    if u'\u4e00' <= str <= u'\u9fff':
        return True
    return False


def isEnglish(uchar):
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False


def word_split_out(text):
    word_list = []
    wcurrent = []

    for i, c in enumerate(text):
        if c.isalnum():
            wcurrent.append(c)
        elif wcurrent:
            word = u''.join(wcurrent)
            word_list.append(word)
            wcurrent = []

    if wcurrent:
        word = u''.join(wcurrent)
        word_list.append(word)

    return word_list


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
        self.lyricIndex = {}

        self.filenames = files
        self.file_to_terms = self.process_files()
        # self.regdex = self.regIndex()
        # self.totalIndex = self.execute()
        # self.vectors = self.vectorize()
        # self.mags = self.magnitudes(self.filenames)



    def process_files(self):

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
            singerWordBox = word_split_out(singerName)
            for item in singerWordBox:
                if isChinese(item[0]):
                    for char in item:
                        if char in self.singerIndex.keys():
                            self.singerIndex[char].append(cntSinger)
                        else:
                            self.singerIndex[char] = [cntSinger]
                elif isEnglish(item[0]):
                    if item in self.singerIndex.keys():
                        self.singerIndex[item].append(cntSinger)
                    else:
                        self.singerIndex[item] = [cntSinger]
            cntSinger += 1
        self.singersSize = cntSinger

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

            albumWordBox = word_split_out(albumName)
            for item in albumWordBox:
                if isChinese(item[0]):
                    for char in item:
                        if char in self.albumIndex.keys():
                            self.albumIndex[char].append(cntAlbum)
                        else:
                            self.albumIndex[char] = [cntAlbum]
                elif isEnglish(item[0]):
                    if item in self.albumIndex.keys():
                        self.albumIndex[item].append(cntAlbum)
                    else:
                        self.albumIndex[item] = [cntAlbum]
            cntAlbum += 1
        self.albumsSize = cntAlbum




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
            songLyric = songItem['songLyric']
            self.songIDTable[songID] = cntSong
            # process lyric
            lyricWordBox = word_split_out(songLyric)
            for item in lyricWordBox:
                if isChinese(item[0]):
                    for char in item:
                        if char in self.lyricIndex.keys():
                            self.lyricIndex[char].append(cntSong)
                        else:
                            self.lyricIndex[char] = [cntSong]
                elif isEnglish(item[0]):
                    if item in self.lyricIndex.keys():
                        self.lyricIndex[item].append(cntSong)
                    else:
                        self.lyricIndex[item] = [cntSong]

            # process songName
            songWordBox = word_split_out(songName)
            for item in songWordBox:
                if isChinese(item[0]):
                    for char in item:
                        if char in self.songIndex.keys():
                            self.songIndex[char].append(cntSong)
                        else:
                            self.songIndex[char] = [cntSong]
                elif isEnglish(item[0]):
                    if item in self.songIndex.keys():
                        self.songIndex[item].append(cntSong)
                    else:
                        self.songIndex[item] = [cntSong]
            cntSong += 1



        self.songsSize = cntSong

        ccc =4
        ccc =5

if __name__ == "__main__":
    # print(isChinese("你"))
    index = BuildIndex(["artistJ.json", "albumJ.json", "songJ.json"])
