import json
import os
import subprocess
from pathlib import PurePath

import click


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which
    from shutil import which

    return which(name) is not None


def force_kibana_root():
    if not is_kibana_repo():
        raise click.ClickException("You must run this command in the root of a kibana repo clone")


def is_kibana_repo():
    if not os.path.isfile('package.json'):
        return False

    file = open('package.json')
    try:
        content = json.load(file)
        if content['name'] != 'kibana' or not content['homepage'].startswith('https://www.elastic.co/'):
            return False
    except ValueError:
        return False
    finally:
        file.close()

    return True


def get_modified_files():
    files = ""
    try:
        files = subprocess.getoutput('git diff --name-only HEAD')
    except ValueError:
        return []

    files = filter(None, files.split('\n'))
    return list(files)


def find_related_test(file):
    path = PurePath(file)

    # skip if the file is a test
    if path.match('*.test.*'):
        return ""

    test_file = path.with_suffix('.test' + path.suffix)

    if os.path.isfile(test_file):
        return test_file

    return ""


def find_related_plugin_folder(file):
    path = PurePath(file)

    try:
        if not path.relative_to('x-pack/plugins'):
            return ""
    except ValueError:
        return ""

    while not path.match('x-pack/plugins/*'):
        path = PurePath(path.parent)

    return str(path)


def merge_params(config_params, unparsed_args):
    final_params = []
    params_map = {}
    for conf, value in config_params:
        params_map["--" + conf] = value

    skip = False
    for index, param in enumerate(unparsed_args):
        if skip:
            skip = False
            continue
        nextIsValue = len(unparsed_args) > index + 1 and not str(unparsed_args[index + 1]).startswith('--')
        if param in params_map and nextIsValue:
            params_map[param] = unparsed_args[index + 1]
            skip = True
        else:
            params_map[param] = unparsed_args[index + 1] if nextIsValue else ''
            if nextIsValue:
                skip = True

    for param in params_map:
        final_params.append(param)
        if len(params_map[param]) > 0:
            final_params.append(params_map[param])

    return final_params


def unparsed_to_map(params):
    params_map = {}
    skip = False
    for index, param in enumerate(params):
        if skip:
            skip = False
            continue
        nextIsValue = len(params) > index + 1 and not str(params[index + 1]).startswith('--')
        if param.startswith('--'):
            if nextIsValue:
                params_map[param] = params[index + 1]
                skip = True
            else:
                params_map[param] = ''
    return params_map
