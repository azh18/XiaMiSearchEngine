import os
import buildindex
import pymysql

db_ip = 'localhost'
db_ip = 'localhost'
db_user = 'root'
db_pwd = '879034'
db_database = 'Xiami'
# db_sock = '/home/mysql/mysql.sock'
db_sock = '/var/lib/mysql/mysql.sock'
db = pymysql.connect(host=db_ip, user=db_user, passwd=db_pwd,
                     db=db_database, port=3306)


# db_ip = '202.120.37.78'
# db_user = 'admin'
# db_pwd = '2016_NRL_admin123'
# db_database = 'Xiami'
# # db_sock = '/home/mysql/mysql.sock'
# db_sock = '/var/lib/mysql/mysql.sock'
# db = pymysql.connect(host=db_ip, user=db_user, passwd=db_pwd,
#                      db=db_database, unix_socket=db_sock, port=10002)


sqlSong = """create table songs(
songIdx INTEGER PRIMARY KEY,
songName VARCHAR(200),
songID VARCHAR(20),
songLyric VARCHAR(20000),
songAlbum VARCHAR(100),
songAlbumID VARCHAR(20),
songSinger VARCHAR(100),
songSingerID VARCHAR(20),
songShareNum INTEGER,
songCommentNum INTEGER,
songRealID VARCHAR(20))
"""

sqlAlbum = """create table albums(
albumIdx integer primary key,
albumName varchar(100),
albumID varchar(20),
artistName varchar(20),
artistID varchar(20),
albumListen integer,
albumFansNum integer,
albumCommentNum integer,
albumPict varchar(100)
)

"""

sqlSinger = """create table singers(
artistIdx integer primary key,
artistName varchar(100),
artistID varchar(20),
artistFansNum integer,
artistCommentNum integer,
artistPict varchar(100)
)

"""

cursor = db.cursor()
cursor.execute(sqlSong)
cursor.execute(sqlAlbum)
cursor.execute(sqlSinger)
data = cursor.fetchall()
print(data)