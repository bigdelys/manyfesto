# Manyfesto documentation

The main idea behind the Manyfesto is simple: at each level of a file hierarchy, a special `manifest.yaml` file is placed which contains (key:value) pairs that are assigned to all files in the folder and its subfolders. Manifest files in subfolders overwrite keys assigned in parent directories:

<div align="center">
  <img src="/manyfest_folders.svg" width="700">
</div>

## Dictionary merge policy

When processing YAML dictionaries (similar to Python dictionaries or JavaScript objects), for example:

```yaml
key_x:
    field_y:
      value: 1
    
    field_z:
      value: 2
```

if the child manifest file has the same key and it is also a dictionary, instead of wholly overwriting the parent key, Manyfesto merges the two: only the fields in the structure that are explicitly defined in
the child manifest are overwritten. For example, if the following YAML dictionary is read as the child of the parent YAML displayed above:

```yaml
key_x:
    field_y:
      value: 10
```
the result will be (i.e. files in the folder will be assigned metadata as):

```yaml
key_x:
    field_y:
      value: 10   # overwritten
    
    field_z:      # kept from the parent
      value: 2
```
  
This behavior allows you to more easily fine-tune hierarchical metadata while keeping inherited values.
The same merge policy also applies to `key: value` pairs defined by directives. Child manifests fully overwrite parent keys when they have non-dictionary (e.g. string, number or list) values.

## Directives
Directive are special key names that are interpreted differently by Manyfesto in order to provide a number of functions.
These directives are often not assigned verbatim as `key:value` pairs. However, similar to other metadata, they are inherited to subfolders and may be overwritten by manifest files inside subfolders. 

## File and Folder matching

`(key: value)` pairs can be selectively assigned to subsets of files based on file/folder patterns (wildcards) in manifest files using the `(match)` directive:

```yaml
(match 200_Hz/*.xml):
   key 1: value 1
   key 2: value 2 

(match *.m):
   key 1: value 3
   key 3: value 4

(match abc.xyz):
   key 2: value 5
   key 4: value 6
```
 
Any key with the format `(match some_pattern)` is interpreted as a directive. The matching pattern should follow GNU/Linux Standard Wildcards (i.e. globbing patterns, [see here](http://www.tldp.org/LDP/GNU-Linux-Tools-Summary/html/x11655.htm)) and can match files, folders or combination of file and folders. 
Folder above the root folder of the container are excluded in file paths during this match process in order to make Manyfesto containers portable, i.e.  to result in the same behaviour regardless of their location in the user file system.

Folder matching enables the efficient use of folders to set particular key values, e.g. all data files with the same sampling rate can be placed in a folder named `256_Hz`, under which data from `healthy` and `patient` groups placed under subfolders with these names. Then the following set of directives 
```yaml
(match /256_Hz/*):
   sampling_rate: 256   

(match /*/healhy/*):
   is_healthy: True   

(match /*/patient/*):
   is_healthy: False   
```

will assign `sampling_rate` and `is_healthy` metadata keys to these files.

## Key-value extraction from folder and filenames

`(key: value)` pairs can be extracted directly from file and folder names via the use of the `(extract)` directive. 
For example

```yaml
(extract sometitle_S[subjectNumber]_T[taskLabel].*): direct
```

matches all files that adhere to the above pattern and extracts values for the specified keys (`subjectNumber` and `taskLabel`) that are enclosed in `[ ]`.
For example, the result of applying the above extract directive to the file: `sometitle_S56_Teyes-open.ext` is
```yaml
   subjectNumber: '56'
   taskLabel: 'eyes-open'
```

The wildcard character `*` can be used to match an arbitrary-length string. The `direct` value assigned to the `(extract)` directive above means that the extracted values are *directly* assigned to keys. Keys can alternatively be assigned after applying a mapping specified as the value to the `(extract)` directive, for example:

```yaml
(extract sometitle_S[subjectNumber]_T[taskLabel].*):
      taskLabel:
              r: resting
              ec: eyes-closed
              eo: eyes-open
```

Results for the file `sometitle_S56_Tec.ext`
```yaml
   subjectNumber: '56'
   taskLabel: eyes-closed  # 'ec' mapped into 'eyes-closed'
```
The `(extract)` directive treats all key values, including numbers, as strings. When mapping numbers to other values, they must be explicitly indicated as strings, e.g.
```yaml
(extract sometitle_S[subjectNumber]_T[taskLabel].set):
      subjectNumber:
          '123': 1230000
```

Only extraction patterns that contain the `/` character in the at the beginning are compared against full paths (relative to container root folder). If `/` is placed at the end, the pattern is assumed to be a folder (similar to `/*`) and hence to match all files in the folder (including subfolders). For example:

```yaml
(extract subject[subjectNumber]/): direct
```

will assign (subjectNumber: '5') to all the files in subject5/ folder. 
<!--
## Named Tables

Tab-separated value (TSV) tables can be placed in Manyfesto manifest file under (table) directive, as a way to compactly assign values to individual files or wildcard patterns of file and folders. They can also be placed in a separate file pointed to using this directive.

In Manyfesto TSV tables, the first row must contain the keys, starting with (match) directive indicating the subsets of files the following keys are assigned to. Keys and values must be separated by a tab character. If there are multiple tables present in a manifest file, each table needs to have a unique name, included as (table name). Example for a single table in the manifest file:

(table): | 
                (match)	key1	key2
                 *.m	value1 	value2
                 File1.set	value3	  value4


Example for multiple tables in a manifest file:

(table abc): | 
                (match)	key1	key2
                 *.m	value1 	value2
                 File1.set	value3	  value4

(table xyz): | 
                (match)	key10	key20
                 *.txt	value10 	value20
                 group\	value30	  value40

External tables (table content in a different file) can be specified as:

(table xyz): [filename, with a path relative to the manifest file]

e.g. 

(table xyz): fileSubjects.tsv 

when the table is in the same folder as the manifest file, or 

(table xyz): /tables/fileSubjects.tsv

when it is in the tables/ folder, under the folder containing the manifest file. Supported format for tables are .tsv (tab separated values) or spreadsheet formats (.xls, .xlsx, .xlsb, .xlsm, .xltm, .xltx, .ods). If the external table is a spreadsheet, variable names must be placed on the first row (there should be no empty rows above the table) and the first column of the table should be the first column of the spreadsheet (there should be no empty columns on the left side of the table).

## Folder-only keys

By default Manyfesto propagates (key:value) pairs from each folder to all of its subfolders. (no-subdir) directive prevents this behavior for as subset of (key:value) pairs defined under it:

(no-subdir):
   folderOnlyKey: somevalue # this is not applied to subfolders  

Other directive can be placed under (no-subdir) and will only apply to files in the folder (and not subfolders):

(no-subdir):
   folderOnlyKey: somevalue # these are not applied to subfolders 
   (matches *.m):
      Key1: values 1
   (table):
       (match)	key10	key20
         *.txt	value10 	value20
          group\	value30	value40

The key:value pairs assigned under (no-subdir) take precedence over the ones assigned outside it.
-->
## Manyfesto version

It is highly recommended for the version of the Manyfesto schema, to which a manifest file adheres to, is to be specified using the (manyfesto version) directive, as:

(manyfesto version): 1.0.1

This enables parsers to process manifest files according to the appropriate version of the schema. Manyfesto uses Semantic Versioning 2.0.0 (http://semver.org/). 

## Namespace

The namespace for the vocabulary of keys:value pairs used in a manifest file may be specified using the (namespace) directive, e.g. :

(namespace): "http://schema.org/"

This is similar to XML namespaces. The (namespace) directive is interpreted like other keys and assigned to all files to which it applies.

## Ignoring files

You can exclude some files from being processed by Manyfesto container using the `(ignore)` directive (similar to `.gitignore` in Git). Manyfesto parsers will not include these ignored files in the list of files for which `(key: value)` pairs are returned. 
Similar to the `(match)` directive, the `(ignore)` directive accepts wildcard patterns for files and folders, for example:

```yaml
(ignore): "*.tmp"
```

ignores all the files with extension `.tmp`.  Notice that single or double quotes must be used for YAML parser to correctly read strings starting with `*.` You can provide an array of file patterns to be ignored too, for example:

```yaml
(ignore): ["*.tmp", "*.pyc"]
```

## Important Notes:

* All specified paths must use unix-style folder separator `/`. This is to ensure uniform execution across all platforms. Windows-style folder separator ‘\’ will be parsed incorrectly in YAML.
Each directive is initially read as a YAML (key:variable) pair and since YAML readers only return the last value assigned to each key, you should only use a single directive phrase once in each manifest document. For example:
```yaml
(match *.m):
    a: true
…
(match *.m):
    b: true
```

will be read as

```yaml
(match *.m):
    b: true
```

ignoring the first match expression. You should instead group these together:
```yaml
(match *.m):
    a: true
    b: true
```

the same rule applies to other directive, e.g. `(extract)`.

* Directives from parent folders are executed before subfolders (children). For example if we have the following directive at folder `/f1`
```yaml
(match *.set):
   a: 1
   b: 2
```

and have in folder `/f1/f2`
```yaml	
(match *.set):
   a: 10
```
	
then all *.set files will  have 
```yaml	
a:10
b:2
```



