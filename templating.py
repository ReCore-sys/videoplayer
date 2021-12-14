import os
import re
from sanic.response import html, text
from bs4 import BeautifulSoup as bs
from jsmin import jsmin



templatedir = os.path.join(os.path.dirname(__file__), 'templates')

htmldir = os.path.join(templatedir, 'html')
cssdir = os.path.join("static", 'css')
jsdir = os.path.join("jsdir", 'js')

htmldir = htmldir.replace('\\', '&&&')
htmldir = htmldir.replace('/', '&&&')
htmldir = htmldir.replace('&&&', os.path.sep)

def minify(css):
    # remove comments - this will break a lot of hacks :-P
    css = re.sub( r'\s*/\*\s*\*/', "$$HACK1$$", css ) # preserve IE<6 comment hack
    css = re.sub( r'/\*[\s\S]*?\*/', "", css )
    css = css.replace( "$$HACK1$$", '/**/' ) # preserve IE<6 comment hack

    # url() doesn't need quotes
    css = re.sub( r'url\((["\'])([^)]*)\1\)', r'url(\2)', css )

    # spaces may be safely collapsed as generated content will collapse them anyway
    css = re.sub( r'\s+', ' ', css )

    # shorten collapsable colors: #aabbcc to #abc
    css = re.sub( r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)', r'#\1\2\3\4', css )

    # fragment values can loose zeros
    css = re.sub( r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', css )

    for rule in re.findall( r'([^{]+){([^}]*)}', css ):

        # we don't need spaces around operators
        selectors = [re.sub( r'(?<=[\[\(>+=])\s+|\s+(?=[=~^$*|>+\]\)])', r'', selector.strip() ) for selector in rule[0].split( ',' )]

        # order is important, but we still want to discard repetitions
        properties = {}
        porder = []
        for prop in re.findall( '(.*?):(.*?)(;|$)', rule[1] ):
            key = prop[0].strip().lower()
            if key not in porder: porder.append( key )
            properties[ key ] = prop[1].strip()
    return css

def set_template_dir(given_dir: str) -> bool:
    """Sets the directory to look for templates in.

    Parameters
    ----------
    given_dir : str
        The path to the directory to look for templates in.

    Returns
    -------
    bool
        Whether or not the directory was set.

    Raises
    ------
    Warning
        If the directory cannot be found.
    """
    # Homie, idek what im doing here
    if os.path.isdir(given_dir):
        # Stackoverflow says globals are the work of satan. But I am tired. so...
        global templatedir
        templatedir = given_dir
        # Set the other directories
        htmldir = os.path.join(templatedir, 'html')
        return True
    else:
        # Verbally abuse the user
        raise Warning("Directory not found: {}".format(given_dir))
        return False



def template(filepath: str, **kwargs: dict) -> str:
    """template Returns a formatted string from a template file.

    Parameters
    ----------
    filepath : str
        The name of the file to find in the template directory.

    Returns
    -------
    str
        A formatted string from the template file.

    Raises
    ------
    Exception
        If the file cannot be found.
    """
    # By default, the thing worked fine
    status = 200
    # If the status is overridden in the kwargs, use that instead
    if "status" in kwargs:
        status = kwargs["status"]
    # As with the status, headers are None by default
    headers = None
    if "headers" in kwargs:
        headers = kwargs["headers"]
    # Get the filepath to a html thingy
    template_file = os.path.join(htmldir, filepath)
    # If the file does not exist, raise an exception and be sad
    if not os.path.isfile(template_file):
        print("File not found: {}".format(template_file))
        return text(":(\nThe template file got lost", status=404)
    # Open the file and read it
    with open(template_file, 'r') as f:
        # Why did we call it fileinfo? IDFK
        fileinfo = f.read()
        # For all the remaining kwargs, replace the placeholder with the value
        for x in kwargs:
            bracketed = '{{' + x + '}}'
            if bracketed in fileinfo:
                fileinfo = fileinfo.replace(bracketed, str(kwargs[x]))
        # Regex can suck my phat juicy cock
        # Find anything that matches a regex designed to hunt css imports
        fileinfo = re.sub("link rel=\"stylesheet\" href=\"(.*?)\"", r'link rel="stylesheet" href="/static/css/\1"', fileinfo)
        fileinfo = re.sub("script src=\"(.*?)\"", r'script src="/static/js/\1"', fileinfo)

        # Set up beautiful soup
        soup = bs(fileinfo, 'html.parser')
        # Find all tags using lambda bs
        htmltoclean = soup.findAll(lambda tag: not tag.contents)
        # A list of tags to not remove even if they are empty
        noclean = ["br"]
        # Loop through the tags and remove any tag that is empty, not in the noclean list, and has no attributes
        [tag.extract() for tag in htmltoclean if tag.name not in noclean and len(tag.attrs) == 0]
        # Pretty print the soup cos why le fuck not
        fileinfo = soup.prettify()
        # Return this shitscape of HTML code. God I wanna die.
        return html(fileinfo, status, headers)