from setuptools import setup

long_description = "Manyfesto is a data-science tool written in Python. It enables you to to assign meta-data (data about data, as a set of key-value pairs) to each file using a few simple rules. Such meta-data can then be used in data processing scripts, for example to assign class labels when training a machine learning algorithm.\n" \
                   " " \
                   "Folders annotated with Manyfesto are self-describing: instead of writing a document to explain how files are named and organized in folders, a few lines of YAML enables anyone to utilize the data based on the metadata assigned to each file. This makes it easy to share data with others.\n" \
                   " " \
                   "You can think of Manyfesto as 'Markdown for metadata assigment': compared to using JSON or XML to assign metadata for each file, it is simpler, easier to modify and more declarative as it uses rules instead of simply storing a separate sets of metadata for each file.\n" \
                   " " \
                   "The main idea behind the Manyfesto is simple: at any level of the folder hierarchy, a special `manifest.yaml` file containing YAML-formatted text can be placed, containing `(key:value)` pairs that are assigned to all files in the folder and its subfolders. Manifest files in subfolders overwrite keys assigned in parent directories. This is similar to how Cascading Style Sheets (CSS) work. Additionally, a handful of special directives define rules for extracting information from file paths or assigning `(key:value)` pairs to only a subset of files."

setup(name='manyfesto',
      version='0.1.3',
      description='Manyfesto is a data science tools for assigning key-value pairs to individual files using a series of simple rules.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/bigdelys/manyfesto',
      author='Nima Bigdely-Shamlo',
      author_email='manyfesto@gmail.com',
      license='MIT',
      packages=['manyfesto'],
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
                  ],
      keywords='data-science data science metadata yaml manifest',
      install_requires=['pyyaml>=5.1', 'oyaml>=0.9']
      )
