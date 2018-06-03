import glob
import os
import sys

from torchnlp.datasets.dataset import Dataset
from torchnlp.download import download_file_maybe_extract

from .data_utils import text_preprocess


def imdb_dataset(directory='data/', train=False, test=False, train_directory='train', test_directory='test',
                 extracted_name='aclImdb', check_files=['aclImdb/README'],
                 url='http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz', sentiments=['pos', 'neg']):
    """
    Load the IMDB dataset (Large Movie Review Dataset v1.0).

    This is a dataset for binary sentiment classification containing substantially more data than
    previous benchmark datasets. Provided a set of 25,000 highly polar movie reviews for
    training, and 25,000 for testing. There is additional unlabeled data for use as well. Raw text
    and already processed bag of words formats are provided.
    The min length of text about train data is 15, max length of it is 594; The min length
    of text about test data is 42, max length of it is 497.

    **Reference:** http://ai.stanford.edu/~amaas/data/sentiment/

    Args:
        directory (str, optional): Directory to cache the dataset.
        train (bool, optional): If to load the training split of the dataset.
        test (bool, optional): If to load the test split of the dataset.
        train_directory (str, optional): The directory of the training split.
        test_directory (str, optional): The directory of the test split.
        extracted_name (str, optional): Name of the extracted dataset directory.
        check_files (str, optional): Check if these files exist, then this download was successful.
        url (str, optional): URL of the dataset `tar.gz` file.
        sentiments (list of str, optional): Sentiments to load from the dataset.

    Returns:
        :class:`tuple` of :class:`torchnlp.datasets.Dataset`: Tuple with the training dataset and
        test dataset in order if their respective boolean argument is true.

    Example:
        >>> from torchnlp.datasets import imdb_dataset
        >>> train = imdb_dataset(train=True)
        >>> train[0:2]
        [{
          'label': 'Company',
          'text': ' Abbott of Farnham E D Abbott Limited was a British coachbuilding ...'},
         {
          'label': 'Company',
          'text': " Schwan-STABILO is a German maker of pens for writing colouring ..."}]
    """
    download_file_maybe_extract(url=url, directory=directory, check_files=check_files)

    ret = []
    splits = [
        dir_ for (requested, dir_) in [(train, train_directory), (test, test_directory)]
        if requested
    ]
    for split_directory in splits:
        full_path = os.path.join(directory, extracted_name, split_directory)
        examples = []
        text_min_length = sys.maxsize
        text_max_length = 0
        for sentiment in sentiments:
            for filename in glob.iglob(os.path.join(full_path, sentiment, '*.txt')):
                with open(filename, 'r', encoding="utf-8") as f:
                    text = f.readline()
                text = text_preprocess(text)
                if len(text) == 0:
                    continue
                else:
                    if len(text.split()) > text_max_length:
                        text_max_length = len(text.split())
                    if len(text.split()) < text_min_length:
                        text_min_length = len(text.split())
                examples.append({'label': sentiment, 'text': text})
        ret.append(Dataset(examples))
        print('text_min_length:' + str(text_min_length))
        print('text_max_length:' + str(text_max_length))

    if len(ret) == 1:
        return ret[0]
    else:
        return tuple(ret)
