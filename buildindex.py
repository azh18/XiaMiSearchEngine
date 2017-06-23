# -*- coding:utf-8 -*-

# input = [file1, file2, ...]
# res = {filename: [world1, word2]}

import re
import math
import json
import jieba
import pickle
# import dill as pickle
import pymysql
import hickle
import ujson
import dill



# db_ip = '202.120.37.78'
# db_user = 'admin'
# db_pwd = '2016_NRL_admin123'
# db_database = 'Xiami'
# # db_sock = '/home/mysql/mysql.sock'
# db_sock = '/var/lib/mysql/mysql.sock'
# db = pymysql.connect(host=db_ip, user=db_user, passwd=db_pwd,
#                      db=db_database, unix_socket=db_sock, port=10002, charset="utf8")


# db_ip = 'localhost'
db_ip = 'localhost'
db_user = 'root'
db_pwd = '879034'
db_database = 'Xiami'
# db_sock = '/home/mysql/mysql.sock'
# db_sock = '/var/lib/mysql/mysql.sock'
db = pymysql.connect(host=db_ip, user=db_user, passwd=db_pwd,
                     db=db_database, port=3306, charset="utf8")
cursor = db.cursor()



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

        # store linked information (belonging...)
        self.singers = []
        self.albums = []
        self.songs = []
        # the number of singers, albums, ...
        self.singersSize = 0
        self.albumsSize = 0
        self.songsSize = 0
        # store map (songID ---> songIdx)
        self.songIDTable = {}
        self.albumIDTable = {}
        self.singerIDTable = {}
        # store posting list (str ---> Idx)
        self.singerIndex = {}
        self.albumIndex = {}
        self.songIndex = {}
        self.lyricIndex = {}
        # the biggest popular number in db
        self.biggestPopular = 0

        self.filenames = files
        # self.regdex = self.regIndex()
        # self.totalIndex = self.execute()
        # self.vectors = self.vectorize()
        # self.mags = self.magnitudes(self.filenames)



    def process_files(self):
        singerFileName = self.filenames[0]
        cntSinger = 0
        for line in open(singerFileName, 'r', encoding='utf-8'):
            try:
                singerItem = json.loads(line)
            except:
                continue
            #store singer into database
            try:
                sql = "insert into singers(artistIdx, artistName,artistID," \
                      "artistFansNum,artistCommentNum,artistPict)" \
                      "values('%d','%s','%s','%d','%d','%s')" % \
                      (cntSinger, singerItem["artistName"][0], singerItem["artistID"],\
                        int(singerItem["artistFansNum"]), \
                       int(singerItem["artistCommentNum"]), singerItem["artistPict"])
                cursor.execute(sql)

            except Exception as e:
                print(e)


            # process singer
            singerID = singerItem["artistID"]
            self.singerIDTable[singerID] = cntSinger
            singerLink = {}
            singerLink["albumsIdx"] = []
            singerLink["songsIdx"] = []
            self.singers.append(singerLink)
            singerName = singerItem['artistName'][0]
            singerWordBoxRaw = word_split_out(singerName)
            # singerWordBox = jieba.cut_for_search(singerName)
            # for item in singerWordBox:
            #     if item in self.singerIndex.keys():
            #         self.singerIndex[item].append(cntSinger)
            #     else:
            #         self.singerIndex[item] = [cntSinger]

            for item in singerWordBoxRaw:
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
        db.commit()

        albumFileName = self.filenames[1]
        cntAlbum = 0
        for line in open(albumFileName, 'r', encoding='utf-8'):
            try:
                albumItem = json.loads(line)
            except:
                continue
            # store album into database
            try:
                sql = "insert into albums(albumIdx, albumName,albumID,artistName,artistID,albumListen," \
                      "albumFansNum,albumCommentNum,albumPict)"\
                      "values('%d','%s','%s','%s','%s','%d','%d','%d','%s')" % \
                      (cntAlbum, albumItem["albumName"].replace("\'", "\'\'"), albumItem["albumID"], albumItem["artistName"][0], albumItem["artistID"],\
                       int(albumItem["albumListen"]), int(albumItem["albumFansNum"]), \
                       int(albumItem["albumCommentNum"]), albumItem["albumPict"])
                cursor.execute(sql)


            except Exception as e:
                print(e)

            albumLink = {}
            albumBelongsToSingerID = albumItem["artistID"]
            if albumBelongsToSingerID in self.singerIDTable.keys():
                albumLink["singerIdx"] = self.singerIDTable[albumBelongsToSingerID]
                # print(self.singers[albumItem["singerIdx"]])
                self.singers[albumLink["singerIdx"]]["albumsIdx"].append(cntAlbum)
            # process songs
            albumLink["songsIdx"] = []
            # process album
            albumID = albumItem["albumID"]
            self.albumIDTable[albumID] = cntAlbum

            self.albums.append(albumLink)
            albumName = albumItem['albumName']

            # albumWordBox = jieba.cut_for_search(albumName)
            # for item in albumWordBox:
            #     if item in self.albumIndex.keys():
            #         self.albumIndex[item].append(cntAlbum)
            #     else:
            #         self.albumIndex[item] = [cntAlbum]

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
        db.commit()




        songFileName = self.filenames[2]
        cntSong = 0
        for line in open(songFileName, 'r', encoding='utf-8'):
            try:
                songItem = json.loads(line)
            except:
                continue

            # clean invalid song (artist is not in artistDB)
            if len(songItem["songSingerID"]) == 0:
                continue
            elif songItem["songSingerID"][0] not in self.singerIDTable.keys():
                continue
            # store songs into database
            try:
                sql = "insert into songs(songIdx, songName,songID,songLyric,songAlbum,songAlbumID,songSinger,\
                songSingerID,songShareNum,songCommentNum,songRealID)"\
                      "values('%d','%s','%s','%s','%s','%s','%s','%s','%d','%d','%s')" % \
                      (cntSong, songItem["songName"].replace("\'", "\'\'"), songItem["songID"],
                       songItem["songLyric"].replace("\'", ""), songItem["songAlbum"].replace("\'", "\'\'"),
                       songItem["songAlbumID"], songItem["songSinger"][0].replace("\'", "") if len(songItem["songSinger"]) else "",
                       songItem["songSingerID"][0] if len(songItem["songSingerID"]) else "",
                       int(songItem["songShareNum"]), int(songItem["songCommentNum"]),
                       songItem["songRealID"])
                cursor.execute(sql)

            except Exception as e:
                print(e)

            songLink = {}
            rating = int(songItem["songCommentNum"]) + int(songItem["songShareNum"])
            if rating > self.biggestPopular:
                self.biggestPopular = rating
            songBelongToAlbumID = songItem["songAlbumID"]
            if songBelongToAlbumID in self.albumIDTable.keys():
                songLink["albumIdx"] = self.albumIDTable[songBelongToAlbumID]
                self.albums[songLink["albumIdx"]]["songsIdx"].append(cntSong)
            songBelongToSingerID = songItem["songSingerID"][0]
            if songBelongToSingerID in self.singerIDTable.keys():
                songLink["singerIdx"] = self.singerIDTable[songBelongToSingerID]
                self.singers[songLink["singerIdx"]]["songsIdx"].append(cntSong)

            self.songs.append(songLink)
            songName = songItem['songName']
            songID = songItem['songID']
            songLyric = songItem['songLyric']
            self.songIDTable[songID] = cntSong
            # process lyric
            # lyricWordBox = jieba.cut_for_search(songLyric, HMM=False)
            # for item in lyricWordBox:
            #     if item in self.lyricIndex.keys():
            #         self.lyricIndex[item].append(cntSong)
            #     else:
            #         self.lyricIndex[item] = [cntSong]
            # posting list with positions
            lyricWordBox = word_split_out(songLyric)
            position = 0
            for item in lyricWordBox:
                if isChinese(item[0]):
                    for char in item:
                        if char in self.lyricIndex.keys():
                            if cntSong in self.lyricIndex[char].keys():
                                self.lyricIndex[char][cntSong].append(position)
                                # self.lyricIndex[char][cntSong] = position
                            else:
                                self.lyricIndex[char][cntSong] = [position]
                                # self.lyricIndex[char] = {cntSong: position}
                        else:
                            self.lyricIndex[char] = {}
                            self.lyricIndex[char][cntSong] = [position]
                        position += 1

                elif isEnglish(item[0]):
                    if item in self.lyricIndex.keys():
                        if cntSong in self.lyricIndex.keys():
                            self.lyricIndex[item][cntSong].append(position)
                        else:
                            self.lyricIndex[item][cntSong] = [position]
                    else:
                        self.lyricIndex[item] = {}
                        self.lyricIndex[item][cntSong] = [position]
                    position += 1

            # process songName
            # songWordBox = jieba.cut_for_search(songName)
            # for item in songWordBox:
            #     if item in self.songIndex.keys():
            #         self.songIndex[item].append(cntSong)
            #     else:
            #         self.songIndex[item] = [cntSong]

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
        db.commit()
        self.songsSize = cntSong



        ccc =4
        ccc =5

    def serialize(self, fileName):
        pickle.dump(self, open(fileName, 'wb'))
        # hickle.dump(self, fileName, mode='w')
        # ujson.dump(self, open(fileName, 'w'))
        # ujson.dump(self.singers, open("singers.data", 'w'))
        # ujson.dump(self.albums, open("albums.data", 'w'))
        # ujson.dump(self.songs, open("songs.data", 'w'))
        # pickle.dump([self.singersSize, self.albumsSize, self.songsSize], open("singersSize.data", 'w'))
        # ujson.dump(self.songIDTable, open("songIDTable.data", 'w'))
        # ujson.dump(self.albumIDTable, open("albumIDTable.data", 'w'))
        # ujson.dump(self.singerIDTable, open("singerIDTable.data", 'w'))
        # ujson.dump(self.singerIndex, open("singerIndex.data", 'w'))
        # ujson.dump(self.albumIndex, open("albumIndex.data", 'w'))
        # ujson.dump(self.songIndex, open("songIndex.data", 'w'))
        # ujson.dump(self.lyricIndex, open("lyricIndex.data", 'w'))


    def deserialize(self, fileName):
        return pickle.load(open(fileName, 'rb'))
        # self.singers = ujson.load(open("singers.data", 'r'))
        # self.albums = ujson.load(open("albums.data", 'r'))
        # self.songs = ujson.load(open("songs.data", 'r'))
        # self.singersSize = ujson.load(open("singersSize.data", 'r'))[0]
        # self.albumsSize = ujson.load(open("singersSize.data", 'r'))[1]
        # self.songsSize = ujson.load(open("singersSize.data", 'r'))[2]
        # self.songIDTable = ujson.load(open("songIDTable.data", 'r'))
        # self.albumIDTable = ujson.load(open("albumIDTable.data", 'r'))
        # self.singerIDTable = ujson.load(open("singerIDTable.data", 'r'))
        # self.singerIndex = ujson.load(open("singerIndex.data", 'r'))
        # self.albumIndex = ujson.load(open("albumIndex.data", 'r'))
        # self.songIndex = ujson.load(open("songIndex.data", 'r'))
        # self.lyricIndex = ujson.load(open("lyricIndex.data", 'r'))

if __name__ == "__main__":
    # print(isChinese("你"))
    index = BuildIndex(["artistJ.json", "albumJ.json", "songJ.json"])
    index.process_files()
    index.serialize("index.data")
