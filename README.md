# treetagger-xml

This is a simple script (`process.py`) that reads in a .xml-file in the [OPUS format](http://opus.nlpl.eu/), uses [TreeTagger](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) to parse/lemmatize each sentence, an appends this information to the word elements in the original .xml-file.
The script also facilitates tagging a .txt-file and then converting the tab-separated output from TreeTagger to the OPUS format.

## Requirements

### TreeTagger

See [the TreeTagger website](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) for installation instructions. Note that you'll have to download a paramater file for each language you would want to tag/lemmatize. This script has been tested on version 3.2.1 of TreeTagger.

### Python

This script runs in Python 3 and requires two external packages to run: [lxml](http://lxml.de/) and [treetaggerwrapper](http://treetaggerwrapper.readthedocs.io/en/latest/). The latter requires [six](https://pythonhosted.org/six/) to be installed as well. You can install these packages either locally (in a [virtualenv](http://virtualenv.readthedocs.io/en/latest/)) or globally via running:

	pip install -r requirements.txt

## Running the script

Before running the script, it's best to set an environment variable with the location of TreeTagger. The treetaggerwrapper tries to detect the installation automatically, but this is not fool-proof. You can set the environment variable (under Linux) with:

	export TAGDIR=/opt/treetagger/

Alternatively, you can modify `process.py` and hard-code your installation path in the TreeTagger instantation.

Then, you can run the `process.py` script. It requires three parameters: your input format (xml or txt), your language of choice for parsing and lemmatizing, and your input file(s). In the `examples/` directory you can find some example .xml-files. Run

	python process.py xml en examples/en.xml

to process the English example. The resulting file will be named `examples/en-out.xml`.

### Processing plain text

Processing plain text requires you to set the first argument to `txt` rather than `xml`. For example:

    python process.py txt en examples/en.txt
    
This script will output a tab-separated file (`examples/en.tab`) as well as an .xml-file in the OPUS format (`examples/en.xml`).
