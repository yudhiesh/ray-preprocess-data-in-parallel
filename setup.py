import setuptools

setuptools.setup(
    name="yudhiesh",  # Replace with your own username
    version="0.0.1",
    author="Manning",
    description="News Category",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pygit2==1.6.0',
        'aiohttp==3.7.4',
        'dataclasses==0.7',
        'gensim==4.0.1',
        'beautifulsoup4',
        'h5py==3.1.0',
        'nltk==3.6.2',
        'numpy==1.19.2',
        'unidecode==1.2.0',
        'ray[default]==1.6.0',
        'pyre-check==0.9.3',
        'pylint==2.8.2',
        'pydantic>=1.8',
        'python-Levenshtein',
        'numba',
        'scikit-learn',
        'future_annotations',
        'cloudpickle',
        'transformers',
        'pandas',
    ],
)
