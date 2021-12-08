import os
import sys
import random
import time
import ujson as json


templatedir = os.path.join(os.path.dirname(__file__), 'templates')

def set_template_dir(given_dir):
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
    if os.path.isdir(given_dir):
        global templatedir
        templatedir = given_dir
        return True
    else:
        raise Warning("Directory not found: {}".format(given_dir))
        return False


def template(filepath, **kwargs):
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
    template_file = os.path.join(templatedir, filepath)
    if not os.path.isfile(template_file):
        raise Exception("File not found: {}".format(template_file))
    with open(template_file, 'r') as f:
        fileinfo = f.read()
        for x in kwargs:
            bracketed = '{{' + x + '}}'
            if bracketed in fileinfo:
                fileinfo = fileinfo.replace(bracketed, str(kwargs[x]))
        return fileinfo