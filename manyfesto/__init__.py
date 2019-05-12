import os
import oyaml
from collections import OrderedDict, namedtuple
from typing import List, Tuple, Union, Dict
import copy
from pathlib import PurePath

# current version
DEFAULT_MANIFEST_FILE = 'manifest.yaml'
MATCH_DIRECTIVE = 'match'
IGNORE_DIRECTIVE = 'ignore'
EXTRACT_DIRECTIVE = 'extract'
MANIFEST_FILENAME_DIRECTIVE = 'manifest filename'

# future directives
TABLE_DIRECTIVE = 'table'
NO_SUBDIR_DIRECTIVE = 'no-subdir'
VERSION_DIRECTIVE = 'manyfesto version'
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


def _get_file_key_value_directives(folder: str, context: Context = None, verbosity=True) -> \
        Tuple[Dict[str, KeyValuesAndDirectives], List, List]:
    """
    Internal
    :param folder:
    :param context:
    :param verbosity:
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
            current_folder_manifest_odict = oyaml.load(f)
    else:
        current_folder_manifest_odict = OrderedDict()

    # separate directive from simple_key-value pairs
    simple_key_values = OrderedDict()
    directives = list()

    manyfesto_directives = {MATCH_DIRECTIVE, EXTRACT_DIRECTIVE, IGNORE_DIRECTIVE}
    manyfesto_file_level_directives = {MATCH_DIRECTIVE, EXTRACT_DIRECTIVE, IGNORE_DIRECTIVE}

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
                       # table directives to be implemented here
                    pass

        if is_simple_kv:
            simple_key_values[key] = current_folder_manifest_odict[key]

    # update context
    # making sure changes stay local to this function
    current_context = copy.deepcopy(context)

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


def manyfesto(folder: str, return_issues=False, verbosity=True) \
        -> Union[OrderedDict, Tuple[OrderedDict, List, List]]:
    """

    :param folder:
    :param return_issues:
    :param verbosity:
    :return:
    """

    files_key_values_directives, errors, warnings = _get_file_key_value_directives(folder, verbosity=verbosity)

    files_key_values = dict()
    files_to_ignore = set()

    for file in files_key_values_directives:
        file_posix = PurePath(file).as_posix()
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

    if return_issues:
        return files_key_values, errors, warnings
    else:
        return files_key_values

