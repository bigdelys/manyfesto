# Manyfesto
<div align="center">
  <img src="/logo.svg" width="70%">
</div>

Manyfesto is a data-science tool written in Python. It enables you to to assign meta-data (data about data, as a set of key-value pairs) to each file using a few simple rules. Such meta-data can then be used in data processing scripts, for example to assign class labels when training a machine learning algorithm.

## What problem does it solve?
You may be wondering what is the problem Manyfesto tries to solve. Most data-science workflows include a step where the data from a number of different files is read and combined together to form data arrays. As the number of these files increases, it becomes more important to keep them organized and keep track of their metadata. 
For example, imagine you want to create a machine learning system to detect fraudulent transactions. The customer, e.g. a bank, provides you with 
20 files, 15 of them containing legitimate transactions and 5 containing fraudulent ones. Transaction type is encoded in file names, along with some other information (date range). 

So far these files are easy to manage: you can place them in two folders (fraudulent or not), or read write a few lines of code to infer transaction classes from their names at load time.  
During the processing these files, you find some quality issues with a subset of them and report them to the bank. After a while they send you a new set of files with improved processing. 
This new set contains improved versions of the problematic subset plus some new files. But unfortunately it has a slightly different naming convention, different enough that requires new code to process it.


As the project continues, this process repeats a few more times, resulting in multiple folders each containing files with a slightly different naming conventions. 
Now you need to keep track of a number of values for each file: the order it was received form the bank, its naming convention and whether it contains fraudulent transactions.
This is often addressed by having multiple `if/else` statements in the import code. Unfortunately this solution is neither elegant nor very scalable.   

Manyfesto offers an alternative solution: all metadata is obtained in a single line of code by calling Manyfesto. 
To specify how metadata is to be extracted, you create a short YAML file is each folder. Common metadata or extraction rules can be placed on parent folder and 
are inherited to subfolders.       

## Example

It is easier to show what Manyfesto does by an example. If we have a folder called `animals` containing the following files:

```
animals
│ manifest.yaml
│
└─── cat
│    │ persian.jpg
│    │ siamese.png
│
└─── dog
     │ boxer.jpg
     │ corgy.png
```
with `manifest.yaml` as:
```yaml
(extract /[animal]/[breed].*): direct

(match *.png):
  is_png: True

common: 1
```
Manyfesto produces the following output (here presented as YAML, the actual output is a Python dictionary):
```yaml
/cat/persian.jpg:
  common: 1
  animal: cat
  breed: persian
/cat/siamese.png:
  common: 1
  animal: cat
  breed: siamese
  is_png: true
/dog/boxer.jpg:
  common: 1
  animal: dog
  breed: boxer
/dog/corgy.png:
  common: 1
  animal: dog
  breed: corgy
  is_png: true
```
For each file, a set of `(key:value)` pairs is defined, following the rules in the manifest.yaml file. The rule 

```yaml
(extract /[animal]/[breed].*): direct
```

extracts values for `animal` and `breed` keys from filenames. In contrast, `common` key is set to `1` for all files.

```yaml
(match *.png):
  is_png: True
```
assigns the value `True` to `is_png` key only to files that match the glob (wildcard) pattern `*.png`. More examples are available in the `/tests` folder.

Folders annotated with Manyfesto are self-describing: instead of writing a document to explain how files are named and organized in folders, a few lines of YAML enables anyone to utilize the data based on the metadata assigned to each file. This makes it easy to share data with others.  

You can think of Manyfesto as "Markdown for metadata assigment": compared to using JSON or XML to assign metadata for each file, it is simpler, easier to modify and more declarative as it uses rules instead of simply storing a separate sets of metadata for each file. 

The main idea behind the Manyfesto is simple: at any level of the folder hierarchy, a special `manifest.yaml` file containing YAML-formatted text can be placed, containing `(key:value)` pairs that are assigned to all files in the folder and its subfolders. Manifest files in subfolders overwrite keys assigned in parent directories:

<div align="center">
  <img src="/manyfest_folders.svg" width="700">
</div>

This is similar to how Cascading Style Sheets (CSS) work. Additionally, a handful of special directives define rules for extracting information from file paths  (`extract` directive) or assigning `(key:value)` pairs to only a subset of files (`match` directive).

To learn more about Manyfesto please read the documentation.

## Installation
```
>> pip install manyfesto
```
 
 ## How to use
To import a folder containing manifest.yaml files: 
```python
from manyfesto import manyfesto
file_kvs = manyfesto(folder)
```

The output `file_kvs` is a Python dictionary with one key for each file under `folder` and its subfolders. The values for these keys contain the metadata for the files:
```python
file_kvs = {
             '/cat/persian.jpg': {'animal': 'cat', 'breed': 'persian', 'common': 1},
             '/cat/siamese.png': {'animal': 'cat',
                                  'breed': 'siamese',
                                  'common': 1,
                                  'is_png': True},
             '/dog/boxer.jpg': {'animal': 'dog', 'breed': 'boxer', 'common': 1},
             '/dog/corgy.png': {'animal': 'dog',
                                'breed': 'corgy',
                                'common': 1,
                                'is_png': True}}
```

Please refer to the documentation to learn how to create `manifest.yaml` files.