import fuzzywuzzy
import os
import sqlstuff
from fuzzywuzzy import process

filepath = os.path.dirname(os.path.realpath(__file__))

sql = sqlstuff.SQL(f"{filepath}/data.db", "files")


def search(query):
    names = sql.getcollumn("name")
    processed = process.extract(query, names, limit=5)
    fulldetails = []
    for x in processed:
        fulldetails.append(sql.get("name", x[0][0])[0])
    return fulldetails


def formatresults(results):
    formatted = []
    for x in results:
        info = sql.get("name", x[0])[0]
        with open(f"{filepath}/templates/html/searchtemplate.html", "r") as f:
            template = f.read()
            args = {"name": info[0], "fname": info[1],
                    "id": info[2], "progress": info[3],
                    "stat": info[4], "size": info[5],
                    "desc": info[6], "poster": info[7],
                    "len": info[8]}
            for y in args:
                template = template.replace("{{" + y + "}}", args[y])
            formatted.append(template)
    formatted = "\n".join(formatted)
    return formatted
