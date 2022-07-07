import re
from typing import List
import spacy
from spacy.tokens import Doc


class TextPreprocessor:
    """
    Pre process texts

    :param pos_tags_removal: list of PoS tags to remove
    :type pos_tags_removal: List[str]
    :param spacy_model: spaCy model to be used, default is en_core_web_sm
    :param remove_numbers: whether or not to remove numbers from the inputs
    :type remove_numbers: bool
    :param remove_special_chars: whether or not to remove the special characters
    :type remove_special_chars: bool
    :param remove_stopwords: whether or not to remove stopwords
    :type remove_stopwords: bool
    :param lemmatize: whether or not to lemmatize the inputs
    :type lemmatize: bool
    :param tokenize: whether or not to tokenize the inputs
    :type tokenize: bool

    """

    def __init__(
        self,
        pos_tags_removal=None,
        spacy_model=None,
        remove_numbers: bool = True,
        remove_special_chars: bool = True,
        remove_stopwords: bool = True,
        lemmatize: bool = True,
        tokenize: bool = False,
    ) -> None:

        self.remove_numbers = remove_numbers
        self.remove_special_chars = remove_special_chars
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize
        self.tokenize = tokenize
        self.pos_tags_removal = pos_tags_removal

        if not spacy_model:
            self.model = spacy.load("en_core_web_sm")
        else:
            self.model = spacy_model

    @staticmethod
    def download_spacy_model(model="en_core_web_sm"):
        """
        Downloads a spaCy model to be used for preprocessing the text inputs

        """
        print(f"Downloading spaCy model {model}")
        spacy.cli.download(model)
        print("Completed downloading the model")

    @staticmethod
    def load_model(model="en_core_web_sm"):
        """
        Loads and returns a spaCy model

        """
        return spacy.load(model, disable=["ner", "parser"])

    def preprocess_text(self, text: str) -> str:
        """
        Preprocesses a single string

        :param text: text string to clean
        :return: str

        """
        if isinstance(text, str):
            doc = self.model(text)
            return self.__preprocess(doc)
        else:
            raise ValueError("Text must be a str")

    def preprocess_text_lists(self, texts: List[str]) -> List[str]:
        """
        Preprocesses a list of strings

        :param texts: List of texts to preprocess
        :return: List of strings

        """
        return [self.__preprocess(doc) for doc in self.model.pipe(texts)]

    def __preprocess(self, doc: Doc) -> str:

        # POS Tags Removal
        if self.pos_tags_removal:
            tokens = [token for token in doc if token.pos_ not in self.pos_tags_removal]
        else:
            tokens = doc

        # Remove numbers
        if self.remove_numbers:
            tokens = [
                token for token in tokens if not (token.like_num or token.is_currency)
            ]

        # Remove stopwords
        if self.remove_stopwords:
            tokens = [token for token in tokens if not token.is_stop]

        # Remove unwanted tokens
        tokens = [
            token
            for token in tokens
            if not (
                token.is_punct or token.is_space or token.is_quote or token.is_bracket
            )
        ]

        # Remove empty tokens
        tokens = [token for token in tokens if token.text.strip() != ""]

        # Lemmatize
        if self.lemmatize:
            text = " ".join([token.lemma_ for token in tokens])
        else:
            text = " ".join([token.text for token in tokens])

        # Remove non-alphabetic chars

        if self.remove_special_chars:
            text = re.sub(r"[^a-zA-Z\']", " ", text)

        # Remove non-Unicode chars
        text = re.sub(r"[^\x00-\x7F]+", "", text)

        # Tokenize
        if self.tokenize:
            tokenizer = self.model.tokenizer
            tokens = " ".join([token.lower_.strip() for token in tokenizer(text)])
            return tokens

        else:
            return text.lower()
