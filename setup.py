import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="treetagger-xml",
    version="0.1.1",
    author="Martijn van der Klis",
    author_email="m.h.vanderklis@uu.nl",
    description="Reads .xml-files and parses these with TreeTagger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/time-in-translation/treetagger-xml",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Topic :: Text Processing :: Linguistic",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'lxml', 'six', 'treetaggerwrapper'
    ]
)
