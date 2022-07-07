from glob import glob
import logging
from pathlib import Path
from typing import List, Optional

from bs4 import BeautifulSoup
from nltk import tokenize
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import csr_matrix


from src.constants import DATA_DIR, ENCODED_DIR
from src.process_files.text_preprocessor import TextPreprocessor
from src.utils import timer

logging.basicConfig(
    format="%(process)d-%(levelname)s-%(message)s",
    level=logging.INFO,
)


def load_html_files() -> List[str]:
    """
    Return all html files from the data directory
    """
    html_file_path = DATA_DIR / "*/*.html"
    return glob(html_file_path.as_posix())


def get_html_text(file: str) -> str:
    """
    Parse file into soup object and get the text out of relevant sections within
    the html
    """
    page = open(file)
    soup = BeautifulSoup(page.read(), features="html.parser")
    [
        s.extract()
        for s in soup(
            [
                "style",
                "script",
                "[document]",
                "head",
                "title",
            ]
        )
    ]
    return soup.getText()


def extract_text_from_html(html_files: List[str]) -> List[str]:
    """
    Extract relevant text data from the html file
    """
    return [get_html_text(file=file) for file in html_files]


def split_text(texts: List[str]) -> List[List[str]]:
    """
    Split text into sentences
    """
    return [tokenize.sent_tokenize(text) for text in texts]


def tokenize_text(
    texts: List[List[str]], preprocessor: TextPreprocessor
) -> List[List[str]]:
    """
    Tokenize and preprocess text
    """
    return [preprocessor.preprocess_text_lists(text) for text in texts]


def encode_texts(texts: List[List[str]]) -> Optional[csr_matrix]:
    """
    Encode text into numerical representation
    """
    vectorizer = CountVectorizer()
    for text in texts:
        try:
            return vectorizer.fit_transform(text)
        except ValueError:
            None


def save_file(data: Optional[csr_matrix], full_path: str) -> None:
    """
    Saves data to its respective path
    """
    path = Path(full_path)
    category = path.parent.stem
    file_name = path.stem
    category = ENCODED_DIR / category
    category.mkdir(parents=True, exist_ok=True)
    path_to_save = category / f"{file_name}.npy"
    if data is not None:
        logging.info("Saving %s", file_name)
        np.save(path_to_save, data)
    else:
        logging.info("Error saving %s", path_to_save)


@timer(file_path="time_results_file.json")
def main_file_processor() -> None:
    """
    Main function to run preprocess of html files in a sequential manner
    """
    html_files = load_html_files()
    texts = extract_text_from_html(html_files=html_files)
    sentences = split_text(texts=texts)
    model = TextPreprocessor.load_model()
    preprocessor = TextPreprocessor(
        spacy_model=model,
        tokenize=True,
    )
    tokenized_sentences = tokenize_text(
        texts=sentences,
        preprocessor=preprocessor,
    )
    encoded_texts = encode_texts(texts=tokenized_sentences)
    for html_file, encoded_text in zip(html_files, encoded_texts):
        save_file(data=encoded_text, full_path=html_file)
