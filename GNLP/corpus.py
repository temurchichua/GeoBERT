import os
import string
import re
from logger import log
import pprint
# usage of counters : https://docs.python.org/2/library/collections.html
from collections import Counter
import pickle

# emit a warning to the puny Humans
log.info('Welcome to the Georgian NLP toolset demo')

printable = set(string.printable)


def not_printable(word):
    """
    Checks if the string contains the printable symbols
    :param word:
    :return True or False:
    """
    for char in word:
        if char in printable:
            return False
    return True


def sizeof_fmt(file_size, suffix='B'):
    """
    Returns the Human Readable file volume unit from num
    :param suffix: default
    :param file_size: file size in integer
    :return:
    ref: https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(file_size) < 1024.0:
            return "%3.1f%s%s" % (file_size, unit, suffix)
        file_size /= 1024.0
    return "%.1f%s%s" % (file_size, 'Yi', suffix)


class Corpus():
    def __init__(self, stop_words='stops.txt'):

        self.stop_words = set(line.strip() for line in open('stops.txt', encoding='utf-8'))
        self.sequence = []
        self.prepro_sequence = []
        self.tokens = []
        self.counted = {}

    def __repr__(self):
        dictionary = self.__dict__
        try:
            for e in ['stop_words', 'sequence', 'prepro_sequence', 'tokens', 'counted']:
                dictionary[e] = len(dictionary.get(e))
        except Exception as error:
            log.error(error)
        else:
            return pprint.pformat(dictionary, indent=4)

    @classmethod
    def from_file(cls, file_name):
        cls.file_name = file_name
        cls.basedir = os.path.abspath(os.path.dirname(file_name))
        cls.path = os.path.join(cls.basedir, cls.file_name)
        cls.status = os.stat(cls.path)
        cls.file_size = sizeof_fmt(cls.status.st_size)
        return cls()

    def preprocess_text(self, text):
        # Remove all the special characters
        text = re.sub(r'\W', ' ', str(text))
        # remove all single characters
        text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)
        # Remove single characters from the start
        text = re.sub(r'\^[a-zA-Z]\s+', ' ', text)
        # Substituting multiple spaces with single space
        text = re.sub(r'\s+', ' ', text, flags=re.I)
        # Removing prefixed 'b'
        text = re.sub(r'^b\s+', '', text)
        # Converting to Lowercase
        text = text.lower()
        # Lemmatization - missing
        tokens = text.split()
        # tokens = [ilem(word) for word in tokens]
        tokens = [word for word in tokens if not_printable(word)]
        tokens = [word for word in tokens if word not in self.ka_stop]
        tokens = [word for word in tokens if len(word) > 3]

        self.tokens.extend(tokens)

        preprocessed_text = ' '.join(tokens)

        return preprocessed_text

    def file2sequence(self, preprocess=False):
        """"creates sequence of sentences from the file
        :if parameter preprocess = True:
        """
        try:
            log.info(f'ვიწყებ {self.file_name}-ის დამუშავებას')
        except Exception as e:
            log.error(
                'გთხოვთ file2seq მეთოდის გამოყენებამდე ობიექტში დაამატოთ სამუშაო ფაილი ობიექტზე from_file(<path>) მეთოდის გამოყენებით')

        try:
            with open(self.path, mode='r', encoding='utf-8') as text_file:
                for line in text_file:
                    line = line.strip('\n')
                    self.sequence.extend(line)

        finally:
            log.info(f'წინადადების რაოდენობა: {len(self.sequence)}')
            text_file.close()

        if preprocess:
            self.preprocess_sequence()

    def preprocess_sequence(self):
        """
        creates preprocessed copy of sequence stored in object using preprocess_text() method
        """
        for element in self.sequence:
            self.prepro_sequence.append(self.preprocess_text(element))

    def count_tokens(self):
        """counts occurrence of current word in whole corpus"""
        self.counted = Counter(self.tokens)

    def save_corpus(self, name='corpus'):

        # Step 2
        with open(f'{name}.obj', 'wb') as destination_file:
            # Step 3
            pickle.dump(self, destination_file)

    @staticmethod
    def load_corpus(name='corpus'):
        # Step 2
        with open(f'{name}.obj', 'r', encoding='utf-8') as file_location:
            # Step 3
            corp = pickle.load(open('corpus.obj', 'r'), encoding='uft-8')
            return corp


corp = Corpus()
corp.from_file("sample.txt")
corp.file2sequence()
corp.save_corpus()

corp2 = Corpus.load_corpus()
