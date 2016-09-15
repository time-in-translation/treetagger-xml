# treetagger-xml

This is a simple script (`process.py`) that reads in a .xml-file, uses TreeTagger to parse/lemmatize each sentence, and then to output the input file with the tags and lemmata appended to the word elements.

## Requirements

### TreeTagger

See [the TreeTagger website](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) for installation instructions. Note that you'll have to download a paramater file for each language you would want to tag/lemmatize. This script has been tested on version 3.2.1 of TreeTagger.

### Python

This script runs in Python 2.7 and requires two external packages to run: [lxml](http://lxml.de/) and [treetaggerwrapper](http://treetaggerwrapper.readthedocs.io/en/latest/). The latter requires [six](https://pythonhosted.org/six/) to be installed as well. You can install these packages either locally (in a [virtualenv](http://virtualenv.readthedocs.io/en/latest/)) or globally via running:

	pip install -r requirements.txt

## Running the script

Before running the script, it's best to set an environment variable with the location of TreeTagger. The treetaggerwrapper tries to detect the installation automatically, but this is not fool-proof. You can set the environment variable (under Linux) with:

	export TAGDIR=/opt/treetagger/

Alternatively, you can modify `process.py` and hard-code your installation path in the TreeTagger instantation.

Then, you can run the `process.py` script. It requires two parameters: your language of choice for parsing and lemmatizing, and your input file(s). In the `examples/` directory you can find some example .xml-files. Run

	python process.py en examples/en.xml

to process the English example. The resulting file will be named `examples/en-out.xml`.
