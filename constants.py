import os
import sys
import random
import time
import ujson as json
import threading
import sqlite3
import sqlstuff
import tmdbsimple as tmdb
from fuzzywuzzy import process

filepath = os.path.dirname(os.path.realpath(__file__))


def stuff_to_do():
    sql = sqlstuff.SQL(f"{filepath}/data.db", "files")
    tmdb.API_KEY = '02771dc93248080f6f6b04cd35d65a0c'
    db = sqlite3.connect(f"{filepath}/data.db")
    cur = db.cursor()
    cur.execute("SELECT * FROM files")
    data = cur.fetchall()
    for x in data:
        desctoname = {}
        ptoname = {}
        if x[6] == None:
            search = tmdb.Search()
            response = search.movie(query=x[0])
            desc = response['results'][0]['overview']
            for y in response['results']:
                desctoname[y["original_title"]] = y["overview"]
            desc = process.extract(x[0], list(desctoname.keys()), limit=1)
            sql.set("desc", x[2], desctoname[desc[0][0]])
        if x[7] == None:

            search = tmdb.Search()
            response = search.movie(query=x[0])
            poster = response['results'][0]['poster_path']
            for y in response['results']:
                ptoname[y["original_title"]] = y["poster_path"]
            poster = process.extract(x[0], list(ptoname.keys()), limit=1)
            sql.set("poster", x[2], ptoname[poster[0][0]])
        if x[8] == None:
            from pymediainfo import MediaInfo
            media_info = MediaInfo.parse(f"{filepath}/videos/{x[1]}.mp4")
            #duration in milliseconds
            duration_in_ms = media_info.tracks[0].duration
            dur = duration_in_ms / 60000
            if dur < 1:
                dur = dur * 60
                dur = round(dur, 2)
                dur = str(dur) + " Seconds"
            elif dur > 60:
                dur = dur / 60
                dur = round(dur, 2)
                dur = str(dur) + " Hours"
            else:
                dur = round(dur, 2)
                dur = str(dur) + " Mins"

            sql.set("len", x[2], dur)


def run():
    threading.Thread(target=stuff_to_do).start()


if __name__ == "__main__":
    run()
