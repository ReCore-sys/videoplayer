from asyncio import CancelledError
import os
import random
import sys
from threading import Thread
import time

import sanic
import sanic_compress
import ujson as json

import templating
from templating import template
import sqlstuff
import searchhelper

import constants

filepath = os.path.dirname(os.path.realpath(__file__))

templating.set_template_dir(f"{filepath}/templates")

app = sanic.Sanic("Video runner")

sql = sqlstuff.SQL(f"{filepath}/data.db", "files")


@app.get("/")
async def index(request):
    return template("index.html", time=time.time())


@app.get("/static/css/<filename>")
async def static_css(request: sanic.Request, filename: str) -> str:
    """Used for serving static css files"""
    return await sanic.response.file(f"{filepath}/static/css/{filename}")


@app.get("/static/js/<filename>")
async def static_js(request: sanic.Request, filename: str) -> str:
    """Used for serving static js files"""
    return await sanic.response.file(f"{filepath}/static/js/{filename}")


@app.get("/static/img/<filename>")
async def static_img(request: sanic.Request, filename: str) -> str:
    """Used for serving static img files"""
    return await sanic.response.file(f"{filepath}/static/img/{filename}")


@app.route('/video_feed/<videoid>', stream=True)
async def video_feed(request, videoid):
    # Get the video's id from the database
    data = sql.get("id", videoid)
    # If we can find it, return the video as a stream or video file.
    # If the file is under 2GB, return the file. Otherwise stream it.
    # This way we don't have to load the whole video into memory and cook my poor Raspberry Pi
    data = data[0]
    filesize = os.path.getsize(f"{filepath}/videos/{data[1]}.mp4")
    if filesize < 2000000000:
        try:
            with open(f"{filepath}/videos/{data[1]}.mp4", "rb") as f:
                return sanic.response.raw(f.read(), headers={"Content-Type": "video/mp4", "Accept-Ranges": "bytes"})
        except CancelledError as e:
            print("A cancelled error occurred")
    else:
        return await sanic.response.file_stream(
            f"{filepath}/videos/{data[1]}.mp4",
            chunk_size=1024,
            mime_type="application/metalink4+xml",
            headers={
                "Content-Disposition": f'Attachment; filename="{data[0]}.meta4"',
                "Content-Type": "application/metalink4+xml",
                "Accept-Ranges": "bytes"
            },
        )


@app.route('/vid/<videoid>')
async def vid(request, videoid):
    # The frontend part of the video player.
    # If you go to /video_feed/<videoid> you will get a download
    timewatched = sql.get("id", videoid)[0][9]
    return template("vid.html", id=videoid, watched=timewatched)


@app.route('/info/<videoid>')
async def info(request, videoid):
    # For info about a video
    data = sql.get("id", videoid)
    # If we can find it, return the video's info
    data = data[0]
    name, fname, vid, progress, status, size, desc, poster, dur, watched = data
    # Kwargs for dayzzzz
    return template("info.html", name=name, fname=fname, id=vid, progress=progress, size=size, desc=desc, poster=poster, dur=dur, watched=watched)


@app.route('/search/<inp>')
async def search(request, inp):
    # For searching for videos
    # If no search term is given, send back a blank search page
    if inp == "":
        return template("search.html")
    else:
        # If we have a search term, search for it using the searchhelper functions
        # Fuzzy matching go brrrrrt
        res = searchhelper.search(inp)
        formatted = searchhelper.formatresults(res)
        return template("search_res.html", results=formatted)


@app.route("/help")
async def help(request):
    return template("help.html")

if __name__ == "__main__":
    # If we're running this file directly, start the server
    constants.run()
    # Set the compression level. We might not even compress anything, but it can't hurt
    app.config['COMPRESS_LEVEL'] = 9
    # FIX: This is a bug in sanic-compress. It converts js/css into binary, which is not what we want
    # sanic_compress.Compress(app)
    build = False

    def runview():
        import ctypes
        if build:
            os.system("cd ./gostuff && go build -buildmode=c-shared -o web.so web.go ")
        webgo = ctypes.cdll.LoadLibrary('./gostuff/web.so')
        web = webgo.webrunner
        web()
    if False:
        Thread(target=runview).start()
        if os.name == "posix":
            os.system('xdotool windowsize Videoplayer 100% 100%')
    app.run(host="0.0.0.0", port=8000)


"""
import openai

openai.Completion.create(
    model="babbage:ft-user-rpl7enaxchqxo4exkkqyhlod-2021-12-12-05-21-06",
    prompt=YOUR_PROMPT)
"""
