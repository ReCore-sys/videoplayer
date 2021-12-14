import os
import random
import sys
import time

import sanic
import ujson as json

import templating
from templating import template
import requests
import sanic_compress
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
    try:
        with open(f"{filepath}/static/css/{filename}", "r") as f:
            return sanic.response.text(f.read())
    except UnicodeDecodeError:
        with open(f"{filepath}/static/css/{filename}", "rb") as f:
            return sanic.response.text(str(f.read()))


@app.get("/static/js/<filename>")
async def static_js(request: sanic.Request, filename: str) -> str:
    """Used for serving static js files"""
    try:
        with open(f"{filepath}/static/js/{filename}", "r", 1, "utf-8") as f:
            return sanic.response.text(f.read())
    except UnicodeDecodeError:
        print("UnicodeDecodeError")
        with open(f"{filepath}/static/js/{filename}", "rb") as f:
            return sanic.response.text(str(f.read()))


@app.route('/video_feed/<videoid>', stream=True)
async def video_feed(request, videoid):
    data = sql.get("id", videoid)
    if len(data) == 0:
        return sanic.response.text("Video not found")
    else:
        data = data[0]
        return await sanic.response.file_stream(
            f"{filepath}/videos/{data[1]}.mp4",
            chunk_size=1024,
            mime_type="application/metalink4+xml",
            headers={
                "Content-Disposition": f'Attachment; filename="{data[0]}.meta4"',
                "Content-Type": "application/metalink4+xml",
            },
        )


@app.route('/vid/<videoid>')
async def vid(request, videoid):
    return template("vid.html", id=videoid)


@app.route('/info/<videoid>')
async def info(request, videoid):
    data = sql.get("id", videoid)
    if len(data) == 0:
        return sanic.response.text("Video not found")
    else:
        data = data[0]
        name, fname, vid, progress, status, size, desc, poster, dur = data
        return template("info.html", name=name, fname=fname, id=vid, progress=progress, size=size, desc=desc, poster=poster, dur=dur)


@app.route('/search/<inp>')
async def search(request, inp):
    if inp == "":
        return template("search.html")
    else:
        res = searchhelper.search(inp)
        formatted = searchhelper.formatresults(res)
        return template("search_res.html", results=formatted)


@app.route("/help")
async def help(request):
    return template("help.html")

if __name__ == "__main__":
    constants.run()
    app.config['COMPRESS_LEVEL'] = 9
    # sanic_compress.Compress(app)
    app.run(host="0.0.0.0", port=8000)


"""
import openai

openai.Completion.create(
    model="babbage:ft-user-rpl7enaxchqxo4exkkqyhlod-2021-12-12-05-21-06",
    prompt=YOUR_PROMPT)
"""
