from nltk import tokenize
import ray
from sklearn.feature_extraction.text import CountVectorizer

from src.process_files.preprocess import (
    get_html_text,
    load_html_files,
    extract_text_from_html,
    save_file,
)
from src.process_files.text_preprocessor import TextPreprocessor
from src.utils import timer

get_html_text_ = ray.remote(get_html_text)
extract_text_from_html_ = ray.remote(extract_text_from_html)
tokenize_ = ray.remote(tokenize.sent_tokenize)
save_file_ = ray.remote(save_file)


@ray.remote
def preprocessor_(preprocessor, sentence):
    return preprocessor.preprocess_text_lists(sentence)


@ray.remote
def vectorizer_fit(vectorizer, sentence):
    try:
        return vectorizer.fit_transform(sentence)
    except ValueError:
        return None


@ray.remote
def save_files(html_files, encoded_texts):
    for html_file, encoded_text in zip(html_files, encoded_texts):
        save_file(data=encoded_text, full_path=html_file)


@timer(file_path="time_results_file.json")
def main_file_processor_ray() -> None:
    # chunk files in order to parallelise function that works on list of files
    # otherwise only single core will be used
    # html_files = [file for file in chunk_list(load_html_files(), batch_size=1000)]
    # text_ids = [extract_text_from_html_.remote(file) for file in html_files]

    # another option would be to use the function that operates on a single file
    # both approaches take about the same amount of time
    # but I prefer the single function approach as there is less code needed
    html_files = load_html_files()
    text_ids = [get_html_text_.remote(file) for file in html_files]
    sentence_ids = [tokenize_.remote(text_id) for text_id in text_ids]
    model = TextPreprocessor.load_model()
    preprocessor_id = ray.put(
        TextPreprocessor(
            spacy_model=model,
            tokenize=True,
        )
    )
    tokenized_sentences_ids = [
        preprocessor_.remote(
            preprocessor_id,
            sentence,
        )
        for sentence in sentence_ids
    ]
    vectorizer_id = ray.put(CountVectorizer())
    encoded_texts_ids = [
        vectorizer_fit.remote(vectorizer_id, sentence)
        for sentence in tokenized_sentences_ids
    ]
    ray.get(save_files.remote(html_files, encoded_texts_ids))
