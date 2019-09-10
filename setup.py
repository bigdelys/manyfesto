from setuptools import setup

long_description = """
Manyfesto is a data-science tool written in Python. It enables you to to assign meta-data (data about data, as a set of key-value pairs) to each file using a few simple rules. Such meta-data can then be used in data processing scripts, for example to assign class labels when training a machine learning algorithm.


Folders annotated with Manyfesto are self-describing: instead of writing a document to explain how files are named and organized in folders, a few lines of YAML enables anyone to utilize the data based on the metadata assigned to each file. This makes it easy to share data with others.


You can think of Manyfesto as 'Markdown for metadata assigment': compared to using JSON or XML to assign metadata for each file, it is simpler, easier to modify and more declarative as it uses rules instead of simply storing a separate sets of metadata for each file.


Please visit project homepage at http://github.com/bigdelys/manyfesto for more information.
"""

setup(name='manyfesto',
      version='1.0.1',
      description='Manyfesto is a data-science tools for assigning key-value pairs to individual files using a series of simple rules.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/bigdelys/manyfesto',
      author='Nima Bigdely-Shamlo, PhD',
      author_email='nima.manyfesto@gmail.com',
      license='MIT',
      packages=['manyfesto'],
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
                  ],
      keywords='data-science data science metadata yaml manifest',
      python_requires='>=3.6',
      install_requires=['oyaml>=0.9']
      )
