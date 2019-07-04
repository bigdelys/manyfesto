import os
import oyaml
from collections import OrderedDict, namedtuple
from typing import List, Tuple, Union, Dict
import copy
from pathlib import PurePath
import re
import uuid

# current version
DEFAULT_MANIFEST_FILE = 'manifest.yaml'
MATCH_DIRECTIVE = 'match'
IGNORE_DIRECTIVE = 'ignore'
EXTRACT_DIRECTIVE = 'extract'
MANIFEST_FILENAME_DIRECTIVE = 'manifest filename'

# future directives
TABLE_DIRECTIVE = 'table'
NO_SUBDIR_DIRECTIVE = 'no-subdir'
VERSION_DIRECTIVE = 'read version'
# the (namespace) directive is processes like a normal (key: value), hence not included.

Context = namedtuple('Context', ['parent_key_values', 'directives', 'root_folder', 'errors', 'warnings',
                                 'manifest_filename'])

# directives are internally stored as a list of Directive objects for each file.
# key is the key defined in the manifest file.
# value is the value defined in the manifest file.
# manifest_filename is the manifest filename where the directive was defined.
Directive = namedtuple('Directive', ['key', 'value', 'manifest_filename'])

# for each file we record both key-value pairs, and the list of directives
KeyValuesAndDirectives = namedtuple('KeyValuesAndDirectives', ['key_values', 'directives'])


def _extract_pattern_key_values(s: str, extract_pattern: str) -> Union[Dict, None]:
    """
    Extracts (key, values) from the input string based on the provided pattern.
    :param s: input string
    :param extract_pattern: a pattern containing * and [key_x] elements. For example: /dir1/*/animal_[type]_[breed].jpg
    :return: If there is a match, a dictionary with pattern (key, values). Otherwise None
    """

    # replace * chars in extract_pattern with dummy extraction keys
    dummy_keys = list()
    while extract_pattern.find('*') > -1:
        uid = 'dummy' + str(uuid.uuid4()).replace('-', '')
        dummy_keys.append(uid)
        extract_pattern = extract_pattern.replace('*', '[' + uid + ']', 1)

    bracket_extraction_regex = r'\[\w+\]+'

    extract_pattern_parts = re.split(bracket_extraction_regex, extract_pattern)
    extract_glob = re.sub(bracket_extraction_regex, '*', extract_pattern)

    extract_keys = re.findall(bracket_extraction_regex, extract_pattern)
    # remove [ and ]
    extract_keys = list(map(lambda x: x.replace('[', ''), extract_keys))
    extract_keys = list(map(lambda x: x.replace(']', ''), extract_keys))

    extracted_kvs = dict()
    if PurePath(s).match(extract_glob):
        for i, part in enumerate(extract_pattern_parts):
            s = s[len(part):]
            if i + 1 < len(extract_pattern_parts):

                if extract_pattern_parts[i + 1] == '':
                    extracted_kvs[extract_keys[i]] = s
                else:
                    next_index = s.find(extract_pattern_parts[i + 1])
                    if next_index > -1:
                        value = s[:next_index]
                        s = s[next_index:]
                        extracted_kvs[extract_keys[i]] = value

        # remove dummy keys
        for k in dummy_keys:
            extracted_kvs.pop(k)
        return extracted_kvs
    else:
        return None

def _get_file_key_value_directives(folder: str, context: Context = None) -> \
        Tuple[Dict[str, KeyValuesAndDirectives], List, List]:
    """
    Internal function to recursively collect key-value pairs and directives. File-level directives are processed
    outside of this function.
    :param folder: the folder to process
    :param context: information from the parent folder, such as directives, key-value pairs, etc.
    :return:
    """

    if context is None:
        context = Context(parent_key_values=OrderedDict(), directives=list(), root_folder=folder,
                          errors=list(), warnings=list(), manifest_filename=DEFAULT_MANIFEST_FILE)

    errors = list()
    warnings = list()
    files_key_values_directives = dict()

    # load the manifest file (if exists) in the current folder
    manifest_filename = os.path.join(folder, context.manifest_filename)
    if os.path.isfile(manifest_filename):
        with open(manifest_filename, 'r') as f:
            current_folder_manifest_odict = oyaml.safe_load(f)
    else:
        current_folder_manifest_odict = OrderedDict()

    # separate directive from simple_key-value pairs
    simple_key_values = OrderedDict()
    directives = list()

    manyfesto_directives = {MATCH_DIRECTIVE, EXTRACT_DIRECTIVE, IGNORE_DIRECTIVE, MANIFEST_FILENAME_DIRECTIVE}
    manyfesto_file_level_directives = {MATCH_DIRECTIVE, EXTRACT_DIRECTIVE, IGNORE_DIRECTIVE}

    children_manifest_filename = context.manifest_filename

    for key in current_folder_manifest_odict:
        is_simple_kv = True
        for directive in manyfesto_directives:
            if key.find('(' + directive) > -1 and key[-1] == ')':  # key starts with ([directive] and ends with )
                directives.append(Directive(key=key, value=current_folder_manifest_odict[key],
                                            manifest_filename=manifest_filename))
                is_simple_kv = False

                if directive in manyfesto_file_level_directives:
                    continue
                else:  # directive is not a file-level directive and hence needs to be processed here
                       if directive == MANIFEST_FILENAME_DIRECTIVE:
                           children_manifest_filename = current_folder_manifest_odict[key]

        if is_simple_kv:
            simple_key_values[key] = current_folder_manifest_odict[key]

    # update context
    # making sure changes stay local to this function
    #current_context = copy.deepcopy(context)
    current_context = Context(parent_key_values=copy.deepcopy(context.parent_key_values),
                              directives=copy.deepcopy(context.directives),
                              root_folder=context.root_folder,
                              errors=copy.deepcopy(context.errors),
                              warnings=copy.deepcopy(context.warnings),
                              manifest_filename=children_manifest_filename)

    # apply new simple key-values
    for key in simple_key_values:
        current_context.parent_key_values[key] = simple_key_values[key]

    # add thee new directive to the end of context directives list (they will execute last, so they take precedence)
    current_context.directives.extend(directives)

    # get the list of files and folders under the current folder.
    # normalize all paths to POSIX type.
    files = list()
    subfolders = list()
    with os.scandir(folder) as it:
        for entry in it:
            if not entry.name.startswith('.'):
                if entry.is_file():
                    files.append(entry.path)
                elif entry.is_dir():
                    subfolders.append(entry.path)

    # assign inherited key-values to the files in the folder
    for file in files:
        # do not assign key-values to the manyfest file itself.
        if file != manifest_filename:
            files_key_values_directives[file] = KeyValuesAndDirectives(key_values=current_context.parent_key_values,
                                                                       directives=current_context.directives)

    # visit each subfolder and obtain file key-values from it
    for subfolder in subfolders:
        sub_files_key_values, sub_errors, sub_warnings = _get_file_key_value_directives(subfolder, current_context)

        # combine key-values and other vars across folders
        files_key_values_directives.update(sub_files_key_values)
        errors = errors + sub_errors
        warnings = warnings + sub_warnings

    return files_key_values_directives, errors, warnings


def _ordereddict_to_dict(value):
    """
    Convert nested OrderedDict objects to nested dict. It does not support Lists.
    :param value: OrderedDict object
    :return: dict object
    """
    for k, v in value.items():
        if isinstance(v, dict):
            value[k] = _ordereddict_to_dict(v)
    return dict(value)


def read(folder: str, return_issues=False, return_dict=True) \
        -> Union[OrderedDict, Tuple[OrderedDict, List, List]]:
    """
    The main function. Starts from the topmost folder and processes manifest files to output an ordered dictionary
    with key-values assigned to all the files under this folder (including subfolders). The files are represented
    relative to the the input folder.
    :param folder: the top folder to start.
    :param return_issues: whether to return errors and warnings. Default is False.
    :param return_dict: If True, it returns a regular python dict object instead of an OrderedDict object.
    :return: either an ordered dictionary with files as keys and key-values as values. or a tuple
    """

    files_key_values_directives, errors, warnings = _get_file_key_value_directives(folder)

    files_key_values = dict()
    files_to_ignore = set()

    for file in files_key_values_directives:
        file_key_values = files_key_values_directives[file].key_values.copy()
        file_directives = files_key_values_directives[file].directives.copy()

        path_relative_to_root = '/' + str(PurePath(file).relative_to(folder).as_posix())

        for file_directive in file_directives:

            key = file_directive.key   # for example (match *.py)
            directive_parts = key[1:-1].split(' ')  # e.g. ['match', '*.py']
            directive_type = directive_parts[0]  # e.g. 'match'
            if len(directive_parts) == 1:
                directive_param = ''
            else:
                directive_param = directive_parts[1]  # e.g. '*.py'

            # make the path (relative to input 'folder') absolute by adding '/'
            # this allows using absolute pattern matching, like '/*.py',
            # see https://docs.python.org/3/library/pathlib.html#module-pathlib

            # get the folder where the manifest file defined the directive. The directive operates
            # relative to this folder.
            directive_root_folder = PurePath(file_directive.manifest_filename).parent

            path_for_matching = '/' + str(PurePath(file).relative_to(directive_root_folder).as_posix())

            if directive_type == MATCH_DIRECTIVE:
                if PurePath(path_for_matching).match(directive_param):
                    file_key_values.update(file_directive.value)
            elif directive_type == EXTRACT_DIRECTIVE:
                extracted_kvs = _extract_pattern_key_values(path_for_matching, directive_param)
                if extracted_kvs:
                    if file_directive.value == 'direct':
                        file_key_values.update(extracted_kvs)
                    elif type(file_directive.value) is dict:

                        # check to see if all keys in the directive dict are are in extraction keys.
                        for k in file_directive.value:
                            if not k in extracted_kvs:
                                warnings.append('In %s: %s must be one of the extraction keys %s.' \
                                              % (key + ': ' + str(file_directive.value), k,
                                                 str(list(extracted_kvs.keys()))))

                        for k in extracted_kvs:
                            if k in file_directive.value:
                                value_mapper_dict = file_directive.value[k]
                                if extracted_kvs[k] in value_mapper_dict:
                                    file_key_values[k] = value_mapper_dict[extracted_kvs[k]]
                                else:
                                    file_key_values[k] = extracted_kvs[k]
                            else:
                                file_key_values[k] = extracted_kvs[k]
                    else:
                        errors.append('In %s: the value must be either "direct" or nested key-value pairs' \
                                      % (key + ': ' + str(file_directive.value)))
            elif directive_type == IGNORE_DIRECTIVE:
                # ignore can have one or more values, normalize a single string them to a list of length 1
                ignore_values = file_directive.value
                if type(ignore_values) is str:
                    ignore_values = [ignore_values]

                for ignore_value in ignore_values:
                    if PurePath(path_for_matching).match(ignore_value):
                        files_to_ignore.add(path_relative_to_root)
                        # print('path_for_matching:', path_for_matching, 'ignore_value:', ignore_value)

        # the files are recorded as key, with paths relative to the root folder.
        files_key_values[path_relative_to_root] = file_key_values.copy()

    # remove ignored files
    files_key_values = {k: v for k, v in files_key_values.items() if k not in files_to_ignore}

    if return_dict:
        files_key_values = _ordereddict_to_dict(files_key_values)

    if return_issues:
        return files_key_values, errors, warnings
    else:
        return files_key_values

