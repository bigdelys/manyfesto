<div align="center">
  <img src="/logo.svg">
</div>

# Manyfesto

Manyfesto is a data science utility that enables you to to assign meta-data, as a set of key-value pairs, to each of your data files using a few simple rules. For example: 

Such meta-data can then be used in your data processing scripts, for example to select data files based on a particular key value (e.g. age > 18). 
Automated assignment of meta-data also makes it easy to share data with others. 

You can think of Manyfesto as `Markdown` for metadata assigment: it is simpler, easier to modify and more declarative (compared to using JSON or XML). The main idea behind the Manyfesto is simple: at each level of the folder hierarchy, a special `manifest.yaml` file containing YAML-formatted text is placed which contains `(key:value)` pairs that are assigned to all files in the folder and its subfolders. Manifest files in subfolders overwrite keys assigned in parent directories:

![Manyfesto key values in folders](./docs/Manyfesto.png "How Manyfesto works")

Special directives are used to assign `(key:value)` pairs to groups of files, or extract file-specific `(key:value)` pairs, based on file names or paths. Here is an example Manyfesto code:

```
key 1: value 1

(matches *.dat):
   key 1: value 2
   key 2: value 3  

(extract sometitle_S[subjectNumber]_T[taskLabel].h5): direct
```

It first assigns `value 1` to `key 1` of all files in the folder and subfolders. It then, for all `.dat` files, overwrites `key 1` values to `value 3` and assigns `value 3` to `key 2`. Finally, it extracts values for `subjectNumber` and `taskLabel` keys from filenames of files that match `sometitle_S[subjectNumber]_T[taskLabel].h5` pattern.

You can learn from the [Manyfesto Reference](https://docs.google.com/document/d/1H5wdQ3sHHq7DZsGgmdvrhSesr4AiHoaQgkmPe2yojoM/edit?usp=sharing).


