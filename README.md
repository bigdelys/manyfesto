
<div align="center">
  <img src="/logo.svg" width="90%">
</div>

# Manyfesto

Manyfesto is an open-source data-science tool written in Python providing "metadata as code". It enables you to to better organize data files on disk by assigning meta-data (data about data, as a set of key-value pairs) to each file using a few lines of YAML. Such meta-data can then be used in data processing scripts, for example to assign class labels when training a machine learning algorithm.


-> In case you are wondering, the letter "y" in in Manyfesto is not a misspelling: Manyfesto is a mix between the words "Many" and "Manifesto".

## What problem does it solve?
Most data-science workflows include a step where the data from several different files are read and combined to form data arrays. As the number of these files increases, it becomes more important to keep them organized and keep track of their metadata. 
For example, imagine you want to create a machine learning system to detect fraudulent transactions. The customer, e.g., a bank, provides you with 
20 files, 15 of them containing legitimate transactions and 5 containing fraudulent ones. Transaction type is encoded in file names, along with some other information (date range). 

So far these files are easy to manage: you can place them in two folders (`fraudulent` and `legitimate`), or write a few lines of code to infer transaction classes from their names at load time. As you analyze these files, you find some quality issues with a subset of them and report this to the bank. After a while, they send you a new set of files with improved pre-processing. 
This new set contains improved versions of the problematic subset plus some new files. But unfortunately, it has a slightly different naming convention and requires new code to process it.


As the project continues, this process repeats a few more times, resulting in multiple folders, each containing files with a slightly different naming convention. 
Now you need to keep track of several values for each file: the order it was received from the bank, its naming convention and whether it contains fraudulent transactions.
This problem is often addressed by having multiple `if/else` statements and execution branches in the import code. Unfortunately, this solution is neither elegant nor very scalable.   

Manyfesto offers an alternative solution: all metadata is obtained in a single line of code. To specify how metadata is to be extracted, you create a small YAML file is each folder. Common metadata or extraction rules can be placed in the parent folder and are inherited by subfolders.
The advantages of this approach are:
1. It is declarative: metadata `(key:value)` sets and naming conventions are defined alongside the data files. 
2. Inheritance of metadata and rules from parent folders in Manyfesto enables factorization, promoting a more intuitive organization of data files in nested directories.
3. Facilitates data sharing: folders annotated with Manyfesto are self-describing. As long as the meanings of keys and values is understood across parties, there is no need to write a document to explain how files are named and organized in folders.  
4. It is simpler and easier to modify than a JSON or XML document that hard-codes metadata separately for each file. You can think of Manyfesto as "Markdown for metadata assigment". 

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

## How does it work?

At any level of the folder hierarchy, a special `manifest.yaml` file containing YAML-formatted text can be placed, containing `(key:value)` pairs that are assigned to all files in the folder and its subfolders. Manifest files in subfolders overwrite keys assigned in parent directories:
<div align="center">
  <img src="/manyfest_folders.svg" width="700">
</div>

This is similar to how Cascading Style Sheets (CSS) work. Additionally, a handful of special directives (also written as `keys:value` pairs) define rules for extracting information from file paths  (`extract` directive) or assigning `(key:value)` pairs to only a subset of files (`match` directive).

To learn more about Manyfesto please read [the documentation](/docs/README.md).

## Installation
```
>> pip install manyfesto
```
 
## How to use Manyfesto
To import a folder containing manifest.yaml files: 
```python
import manyfesto
file_kvs = manyfesto.read(folder)
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

Please refer to [the documentation](/docs/README.md) to learn how to create `manifest.yaml` files.

## Manyfesto as a data containerization tool

From [this paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4782059/):
> Many fields have successfully employed data containerization to provide simplified and portable interfaces to unstructured or loosely structured data ‘payloads’ in the same way that intermodal shipping containers have revolutionized global commerce by replacing “break bulk” and other modes of transportation that required lengthy, manual handling of cargo [(Levinson, 2008)](http://www.eh.net/page/47/?s=standard), ‘Virtual Machine’ containers have enabled and are now an important basis for cloud computing. Most recently, Linux, and in particular Docker software application containers, have gained significant attention in the software development world. These technologies wrap an application in a complete file system containing code, tools and all the dependencies, e.g., runtime libraries, needed to run the application [(Pahl, 2015)](https://ieeexplore.ieee.org/document/7158965). 

Containerization means domain-specific standardized data packaging. It refers to organizing data files and metadata for using a standardized file structure and metadata encapsulation schema. Practitioners can ship a data container as a single unit and operate on its data using a standardized interface without having to deal with peculiarities of its organization.


Assigning meta-data to individual files located on a conventional filesystem is a basic operation required for all containerization systems, such as ESS, BIDS, and ISA-TAB. This operation can be reformulated as assigning a number of `(key: value)` pairs to each file. Containerization systems differ in 
* Their controlled vocabulary, also know as "ontology". This defines how keys and their values should be understood, i.e. mapped into the concepts specific to each domain.
* The way they encode `(key: value)` pairs: Manyfesto uses YAML, ["EEG Study Schema" (ESS)](http://www.eegstudy.org/) uses XML, ["Brain Imaging Data Structure" (BIDS)](https://bids.neuroimaging.io/) uses JSON and [ISA-TAB](https://isa-tools.org/) uses tab-separated files. 
* How they require files to be organized in subfolders. The prescribed organization of the files should be selected to maximally map to the main concepts in the field, e.g. session in EEG studies (ESS) and Runs in fMRI (BIDS). Another way to look at this organization is to treat it as an optimal factorization, e.g. to use folder structure in a way that files sharing the most meta-data keys are placed under the same folder.

Manyfesto was inspired by the "optimal factorization" principle and the commonalities across data containerization standards in the field of neuroscience. As it offers a general interface for assigning metadata to files, Manyfesto can be used as the basis for new data containerization standards in science and engineering fields by utilizing domain-specific controlled vocabularies.
