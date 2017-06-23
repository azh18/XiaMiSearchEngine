import buildindex
import re
import jieba
from buildindex import BuildIndex

class Query:
    def __init__(self, filenames):
        self.filenames = filenames
        self.index = buildindex.BuildIndex("index.data")
        # self.index = buildindex.BuildIndex.deserialize(self.index, filenames)
        self.index = self.index.deserialize("index.data")
        # {songIdx:click times}
        # 直接用频数的缺点：
        # 1、点的次数多了以后，由于频数都很高，导致方法退化为只看点击次数
        # 因此修改为用频率，但如果直接用频率：
        # 一开始点一下百分比就100%，不合理
        # 因此一开始所有歌曲频率都设置为1，这样就点好几次同一首歌才可以出现偏好
        self.singerPrefer = {}
        self.songPrefer = {}
        self.songPreferTotal = 10 # songPrefer之和
        self.singerPreferTotal = 10 # singerPrefer之和
        # self.index = buildindex.BuildIndex(self.filenames)

    def getSingerFromDB(self, singerIdx):
        sql = "select * from singers where artistIdx=%s" % (singerIdx)
        buildindex.cursor.execute(sql)
        buildindex.db.commit()
        result = buildindex.cursor.fetchall()
        result = result[0]
        singer = {}
        singer["artistIdx"] = result[0]
        singer["artistName"] = result[1]
        singer["artistID"] = result[2]
        singer["artistFansNum"] = result[3]
        singer["artistCommentNum"] = result[4]
        singer["artistPict"] = result[5]
        return singer



    def getAlbumFromDB(self, albumIdx):
        sql = "select * from albums where albumIdx=%s" % (albumIdx)
        buildindex.cursor.execute(sql)
        buildindex.db.commit()
        result = buildindex.cursor.fetchall()
        result = result[0]
        album = {}
        album["albumIdx"] = result[0]
        album["albumName"] = result[1]
        album["albumID"] = result[2]
        album["artistName"] = result[3]
        album["artistID"] = result[4]
        album["albumListen"] = result[5]
        album["albumFansNum"] = result[6]
        album["albumCommentNum"] = result[7]
        album["albumPict"] = result[8]
        return album

    def getSongsFromDB(self, songIdx):
        sql = "select * from songs where songIdx=%s" % (songIdx)
        buildindex.cursor.execute(sql)
        buildindex.db.commit()
        result = buildindex.cursor.fetchall()
        result = result[0]
        song = {}
        song["songIdx"] = result[0]
        song["songName"] = result[1]
        song["songID"] = result[2]
        song["songLyric"] = result[3]
        song["songAlbum"] = result[4]
        song["songAlbumID"] = result[5]
        song["songSinger"] = result[6]
        song["songSingerID"] = result[7]
        song["songShareNum"] = result[8]
        song["songCommentNum"] = result[9]
        song["songRealID"] = result[10]
        return song

    def getSingerIdxFromSongIdx(self, songIdx):
        songItem = self.getSongsFromDB(songIdx)
        singerID = songItem["songSingerID"]
        if singerID in self.index.singerIDTable:
            return self.index.singerIDTable[singerID]
        else:
            return -1

    def songQuery(self, keywords):
        songsImmidiate = []
        keywordsBox = buildindex.word_split_out(keywords)
        newFlag = True
        for item in keywordsBox:
            if buildindex.isChinese(item[0]):
                for char in item:
                    if not newFlag:
                        songsImmidiate = list(set(songsImmidiate).intersection(set(self.index.songIndex[char])))
                    else:
                        songsImmidiate = self.index.songIndex[char]
                        newFlag = not newFlag
            elif buildindex.isEnglish(item[0]):
                if not newFlag:
                    songsImmidiate =  list(set(songsImmidiate).intersection(
                        set(self.index.songIndex[item])))
                else:
                    songsImmidiate = self.index.songIndex[item]
                    newFlag = not newFlag
        return songsImmidiate

    def singerQuery(self, keywords, isFull):
        singerImmidiate = []

        keywordsBox = buildindex.word_split_out(keywords)
        newFlag = True
        for item in keywordsBox:
            if buildindex.isChinese(item[0]):
                for char in item:
                    if char in self.index.singerIndex.keys():
                        if not newFlag:
                            singerImmidiate = list(set(singerImmidiate).intersection(set(self.index.singerIndex[char])))
                        else:
                            singerImmidiate = self.index.singerIndex[char]
                            newFlag = not newFlag
            elif buildindex.isEnglish(item[0]):
                if item in self.index.singerIndex.keys():
                    if not newFlag:
                        singerImmidiate = list(set(singerImmidiate).intersection(
                            set(self.index.singerIndex[item])))
                    else:
                        singerImmidiate = self.index.singerIndex[item]
                        newFlag = not newFlag

        # keywordsBox = jieba.cut_for_search(keywords)
        # for item in keywordsBox:
        #     if len(singerImmidiate):
        #         singerImmidiate = list(set(singerImmidiate).intersection(
        #             set(self.index.singerIndex[item])))
        #     else:
        #         singerImmidiate = self.index.singerIndex[item]
        # for item in singerImmidiate:
        #     print(self.index.singers[item])
        # 要求全名匹配
        if isFull:
            singerFinalResult = []
            for id in singerImmidiate:
                # fetch singer from db
                singerInfo = self.getSingerFromDB(id)
                if singerInfo["artistName"] == keywords:
                    singerFinalResult.append(id)
            return singerFinalResult
        else:
            return singerImmidiate

    def lyricQuery(self, keywords):
        songsImmidiate = []
        # keywordsBox = jieba.cut_for_search(keywords)
        # newFlag = True
        # for item in keywordsBox:
        #     if not newFlag:
        #         songsImmidiate = list(set(songsImmidiate).intersection(
        #             set(self.index.lyricIndex[item])))
        #     else:
        #         songsImmidiate = self.index.lyricIndex[item]
        #         newFlag = not newFlag

        keywordsBox = buildindex.word_split_out(keywords)
        for item in keywordsBox:
            songIdxTempList = []
            if buildindex.isChinese(item[0]):
                candID = []
                cntCh = 0
                for char in item:
                    # char in this loop should be continuous
                    if char in self.index.lyricIndex.keys():
                        candID.append(self.index.lyricIndex[char])
                    cntCh += 1
                startLetterID = candID[0]
                for songIdx in startLetterID:
                    matchIdx = True

                    for i in range(1, cntCh):
                        if songIdx not in candID[i].keys():
                            matchIdx = False
                            break
                    if matchIdx:
                        matchAPos = False
                        for pos in startLetterID[songIdx]:
                            matchThisPos = True
                            for i in range(1, cntCh):
                                if (pos + i) not in candID[i][songIdx]:
                                    matchThisPos = False
                                    break
                            if matchThisPos: # illustrate that all later poses is right for this pos
                                matchAPos = True
                                break
                        if matchAPos:
                            # output this songIdx
                            songIdxTempList.append(songIdx)
                if len(songsImmidiate):
                    songsImmidiate = list(
                        set(songsImmidiate).intersection(set(songIdxTempList)))
                else:
                    songsImmidiate = songIdxTempList

            elif buildindex.isEnglish(item[0]):
                if len(songsImmidiate):
                    songsImmidiate = list(set(songsImmidiate).intersection(
                        set(self.index.lyricIndex[item])))
                else:
                    songsImmidiate = self.index.lyricIndex[item]
        ratingSongs = {}
        for item in songsImmidiate:
            songItem = self.getSongsFromDB(item)
            ratingSongs[item] = (int(songItem["songCommentNum"]) +
                                 int(songItem["songShareNum"])) / self.index.biggestPopular * 45
            if songItem["songName"] == keywords:
                ratingSongs[item] += 10
            else:
                ratingSongs[item] += 1
            # preference on this song
            if item in self.songPrefer.keys():
                ratingSongs[item] += self.songPrefer[item] * 2

                # preference on this singer
                # if self.index.singerIDTable[songItem["songSingerID"]] in self.singerPrefer.keys():
                #    ratingSongs[item] += self.singerPrefer[self.index.singerIDTable[songItem["songSingerID"]]]
        ratingSongs = sorted(ratingSongs.items(), key=lambda item:item[1], reverse=True)
        cnt = 0
        returnSongList = []
        for i in ratingSongs:
            songItem = self.getSongsFromDB(i[0])
            returnSongList.append(songItem)
            print(songItem['songName'])
            cnt += 1
            if cnt > 15:
                break
        return returnSongList

    def singerQueryForSongs(self, keywords):
        singerList = self.singerQuery(keywords, True)
        if len(singerList):
            ratingSongs = {}
            songTemp = self.index.singers[singerList[0]]["songsIdx"]
            if len(songTemp):
                for item in songTemp:
                    songItem = self.getSongsFromDB(item)
                    ratingSongs[item] = (int(songItem["songCommentNum"]) +
                                   int(songItem["songShareNum"]))/self.index.biggestPopular*45
                    if songItem["songName"] == keywords:
                        ratingSongs[item] += 10
                    else:
                        ratingSongs[item] += 1
                    # preference on this song
                    if item in self.songPrefer.keys():
                        ratingSongs[item] += self.songPrefer[item] * 2 / self.songPreferTotal

                    # preference on this singer
                    singerIdx = self.getSingerIdxFromSongIdx(item)
                    if singerIdx in self.singerPrefer.keys():
                       ratingSongs[item] += self.singerPrefer[singerIdx] / self.singerPreferTotal

            ratingSongs = sorted(ratingSongs.items(), key=lambda item:item[1], reverse=True)
            cnt = 0
            returnSongList = []
            for i in ratingSongs:
                songItem = self.getSongsFromDB(i[0])
                returnSongList.append(songItem)
                print(songItem['songName'])
                cnt += 1
                if cnt > 15:
                    break
            return returnSongList
        else:
            return []



    def freeQuery(self, keywords):
        # keywordList1 = jieba.cut_for_search(keywords)
        keywordList2 = buildindex.word_split_out(keywords)
        if len(keywordList2)>=2:
            self.lyricQuery(keywords)
        singerList = self.singerQuery(keywords, False)
        # for item in keywordList2:
        #     if len(singerList):
        #         singerList = list(set(singerList).intersection(
        #                     set(self.index.singerIndex[item])))
        #     else:
        #         singerList = self.index.singerIndex[item]
        if len(singerList):
            ratingSongs = {}
            songTemp = self.index.singers[singerList[0]]["songsIdx"]
            if len(songTemp):
                for item in songTemp:
                    songItem = self.getSongsFromDB(item)
                    ratingSongs[item] = (int(songItem["songCommentNum"]) +
                                   int(songItem["songShareNum"]))/self.index.biggestPopular*45
                    if songItem["songName"] == keywords:
                        ratingSongs[item] += 10
                    else:
                        ratingSongs[item] += 1
                    # preference on this song
                    if item in self.songPrefer.keys():
                        ratingSongs[item] += self.songPrefer[item] * 2 / self.songPreferTotal

                    # preference on this singer
                    singerIdx = self.getSingerIdxFromSongIdx(item)
                    if singerIdx in self.singerPrefer.keys():
                       ratingSongs[item] += self.singerPrefer[singerIdx] / self.singerPreferTotal

            ratingSongs = sorted(ratingSongs.items(), key=lambda item:item[1], reverse=True)
            cnt = 0
            returnSongList = []
            for i in ratingSongs:
                songItem = self.getSongsFromDB(i[0])
                returnSongList.append(songItem)
                print(songItem['songName'])
                cnt += 1
                if cnt > 15:
                    break
            return returnSongList
        else:
            ratingSongs = {}
            songTemp = self.songQuery(keywords)
            if len(songTemp):
                for item in songTemp:
                    songItem = self.getSongsFromDB(item)
                    ratingSongs[item] = (int(songItem["songCommentNum"]) +
                                   int(songItem["songShareNum"]))/self.index.biggestPopular*45
                    if songItem["songName"] == keywords:
                        ratingSongs[item] += 10
                    else:
                        ratingSongs[item] += 1
                    # preference on this song
                    if item in self.songPrefer.keys():
                        ratingSongs[item] += self.songPrefer[item] * 2

                    # preference on this singer
                    # if self.index.singerIDTable[songItem["songSingerID"]] in self.singerPrefer.keys():
                    #    ratingSongs[item] += self.singerPrefer[self.index.singerIDTable[songItem["songSingerID"]]]

            ratingSongs = sorted(ratingSongs.items(), key=lambda item:item[1], reverse=True)
            cnt = 0
            returnSongList = []
            for i in ratingSongs:
                songItem = self.getSongsFromDB(i[0])
                returnSongList.append(songItem)
                print(songItem['songName'])
                cnt += 1
                if cnt > 15:
                    break
            return returnSongList

if __name__ == "__main__":
    # q = Query(["artistJ.json", "albumJ.json", "songJ.json"])
    q = Query("index.data")

    # q.lyricQuery("走三关")
    #q.singerQuery("徐佳莹", True)
    # while(1):
    #     keywords = input()
    #     q.freeQuery(keywords)
    # q.songQuery("Love")
    # q.freeQuery("安静")