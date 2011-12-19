#!/usr/bin/python

__author__ = 'uranpro'

import os
import argparse
import re

# xcodelocalize.py path/to/project 'NSLocalizedString(@"FORMAT_KEY")'

FORMAT_KEY = '%localized_key_is_here%'
RE_LOCALIZED_KEY = '.*?"(.*?)".*?=.*?"(.*?)";.*?'
SOURCE_EXT = ['.h', '.m']
LOCALIZABLE_STRINGS = 'Localizable.strings'

def print_keys(keys):
    for k in keys:
        print '- %s : %s' % (k, keys[k])

def file_names_from_dir(dir_name, extensions = None, search_file_name = None):
    files = []
    for dir_name, dir_names, file_names in os.walk(dir_name):
        for file_name in file_names:
            fn = os.path.join(dir_name, file_name)
            if search_file_name and search_file_name != file_name:
                continue
            if extensions:
                fn_no_ext, ext = os.path.splitext(fn)
                if not ext in extensions:
                    continue
            files.append(fn)

    return files

def remove_exists_keys(src, dst):
    tmp = {}
    for k in src:
        if not k in dst:
            tmp[k] = src[k]

    return tmp

def re_from_format(fmt):
    p1, p2 = fmt.split(FORMAT_KEY)
    return '.*?%s(.*?)%s.*?' % (p1, p2)

def keys_from_file(fn, fmt):
    pattern = re_from_format(fmt)
    with open(fn, 'r') as f:
        content = f.read()

    keys = {}
    r_keys = re.finditer(pattern, content)
    for m_key in r_keys:
        k = m_key.group(1)
        keys[k] = k

    return keys

def keys_from_dir(dir_name, fmt):
    keys = {}
    for fn in file_names_from_dir(dir_name, SOURCE_EXT):
        print fn
        keys.update(keys_from_file(fn, fmt))

    return keys

def append_keys_to_file(fn, keys):
    with open(fn, 'a') as f:
        for k in keys:
            f.write('\n"%s" = "%s";' % (k, keys[k]))

def localized_file_names_from_dir(dir_name):
    return file_names_from_dir(dir_name, search_file_name=LOCALIZABLE_STRINGS)

def localized_keys_from_file(fn):
    with open(fn, 'r') as f:
        content = f.read()

    keys = {}

    r_keys = re.finditer(RE_LOCALIZED_KEY, content)
    for m_keys in r_keys:
        k = m_keys.group(1)
        v = m_keys.group(2)
        keys[k] = v

    return keys

##################################################################### Main

def main():

    # Parse arguments
    # path/to/project/ 'NSLocalizedString(@"FORMAT_KEY")'

    print '\n\nUpdating Localizable.strings from xcode project'
    print 'expample: path/to/project \'NSLocalizedString\\(@"%s",\n\n' % FORMAT_KEY

    parser = argparse.ArgumentParser(description='Updating Localizable.strings from xcode project')

    parser.add_argument('path', help='Path to project')
    parser.add_argument('format',
                        help='How can I get keys from files? Format %s' % FORMAT_KEY)

    args = parser.parse_args()

    project_dir = args.path
    fmt = args.format

    if not os.path.exists(project_dir):
        raise Exception('Path not exists')
    if fmt.find(FORMAT_KEY) < 0:
        raise Exception('Format key %s not found' % FORMAT_KEY)

    print 'Path = %s\nFormat = %s\n' % (project_dir, fmt)

    print 'Searching for keys...'
    keys = keys_from_dir(project_dir, fmt)
    print 'Keys found:'
    print_keys(keys)

    print 'Searching for Localizable.strings file'
    for lfn in localized_file_names_from_dir(project_dir):
        print lfn
        localized_keys = localized_keys_from_file(lfn)
        print 'Localized keys:'
        print_keys(localized_keys)
        tmp = remove_exists_keys(keys, localized_keys)
        print 'Keys to append:'
        print_keys(tmp)
        append_keys_to_file(lfn, tmp)

    print 'Done'

    


if __name__ == '__main__':
    main()