# Imports
import os
import re

from IPython import get_ipython
from tqdm import tqdm
from resources.logger import log
import multiprocessing as mp

# usage of counters : https://docs.python.org/2/library/collections.html
from ftfy import fix_encoding

# Init stuff
# emit a warning to the puny Humans
log.info('Welcome to the Georgian NLP toolset demo')

CPU_CORES = mp.cpu_count()
log.info(f'CPU Core count: {CPU_CORES}')
SUBS = 8
log.info(f'N of SubProcesses: {SUBS}')


# functions
def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def file_path(file_name):
    """generates abs path relative to the Package and modules"""
    # If running from notebook
    if isnotebook():
        cwd = os.getcwd()
        f_path = cwd + file_name
    else:
        data_dir = os.path.abspath('')
        f_path = os.path.join(data_dir, file_name)
    # check if the path exists
    if os.path.exists(f_path):
        return f_path
    else:
        raise FileNotFoundError


def is_not_printable(word, letters_only=True):
    """
    Checks if the string contains the printable symbols
    :param word:
    :param letters_only:
    :return True or False:
    """

    for char in word:
        if char not in letters:
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


numbers = set("0123456789")
symbols = set("!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c")
letters = set('ქწერტყუიოპჭღთასდფგჰჯკლშჟ₾ზხცვბნმძჩ')
printable = set().union(*[numbers, symbols, letters])


class FileToProcess():
    def __init__(self, file_name=None, stop_words="data/stops.txt"):

        if not file_name:
            raise ValueError("Init FileToProcess class with path to the file as file_name argument ")

        self.file_name = file_name
        self.__path = file_path(file_name)
        self.__status = os.stat(self.__path)
        self.__file_object = None

        self.stop_words = set(line.strip() for line in open(file_path(stop_words), encoding='utf-8'))
        self.sequence = []
        self.file_size = sizeof_fmt(self.__status.st_size)

    def load_file(self, max_num_of_lines=-1, file_name=None, append=False):
        if append and file_name:
            f_path = file_path(file_name)
        else:
            f_path = self.__path

        with open(f_path, mode='r', encoding='utf-8') as text_file:
            # Progress bar
            pool = mp.Pool(SUBS)
            with pool:
                description = f"Reading the file: {self.file_name}"
                pool_to_iter = pool.imap_unordered(fix_encoding, text_file)

                pbar = tqdm(pool_to_iter, desc=description)

                n = 0

                for line in pbar:

                    if n == max_num_of_lines:
                        break

                    line = line.strip('\n')
                    self.sequence.append(line)
                    n += 1
        # Finally:
        log.info(f'Number of lines in sequence: {len(self.sequence)}')

    def __preprocess_text(self, text, min_sentence_size=3, min_word_size=2, max_word_size=25):
        """preprocess text for NLP tasks"""
        tokens = text.split()
        if len(tokens) <= min_sentence_size:
            return None
        # Removing prefixed 'b'
        text = re.sub(r'^b\s+', '', text)
        # Url Removal
        text = re.sub(r'http\S+', '', text)
        # Number Removal
        text = re.sub(r"$\d+\W+|\b\d+\b|\W+\d+$", '', text)
        # mail removal
        text = re.sub(r'\S*@\S*\s?', '', text)
        # Remove all the special characters
        text = re.sub(r'\W', ' ', text)
        # remove all single characters
        text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)
        # Remove single characters from the start
        text = re.sub(r'\^[a-zA-Z]\s+', ' ', text)
        # Substituting multiple spaces with single space
        text = re.sub(r'\s+', ' ', text, flags=re.I)
        # Converting to Lowercase
        text = text.lower()
        # Lemmatization - missing
        tokens = text.split()

        index = len(tokens) - 1
        while index >= 0:
            word = tokens[index]
            if is_not_printable(word) or word in self.stop_words or len(word) < min_word_size or len(
                    word) > max_word_size:
                tokens.pop(index)
            index -= 1
        if len(tokens) < min_sentence_size:
            return None

        preprocessed_text = ' '.join(tokens)

        return preprocessed_text

    def _check_and_update(self, index):
        sentence = self.sequence[index]
        if pre_processed_sentence := self.__preprocess_text(sentence):
            # update sentence with preprocessed version
            # log.info(f"replaceing: {self.sequence[index]} > {pre_processed_sentence}")
            self.sequence[index] = pre_processed_sentence
        else:
            # pop sentence from sequence
            # log.info(f"popping: {self.sequence[index]} ")
            self.sequence.pop(index)

    def pre_process(self):
        index = len(self.sequence) - 1
        log.info(f'Number of lines before pre-pro: {index}')
        scope = range(index, -1, -1)
        # Progress bar

        pool = mp.Pool(SUBS)
        with pool:
            description = f"Pre-processing the file: {self.file_name}"
            pool_to_iter = pool.imap_unordered(self._check_and_update, scope)
            pbar = tqdm(pool_to_iter, total=index, desc=description)
            for _ in pbar:
                pass
            log.info(f'Number of lines after pre-pro: {len(self.sequence)}')

    def save_to_file(self, filename=None):
        if filename:
            file_name = file_path(filename)
        else:
            file_name = f"{self.__path.split('.')[0]}_pre_processed.txt"

        with open(file_name, 'w', encoding="utf-8") as output:
            # Progress bar
            pbar = tqdm(self.sequence)
            pbar.set_description(f"Saving to the file: {self.file_name}")
            for sentence in pbar:
                output.write(str(sentence) + '\n')

    def __len__(self):
        return len(self.sequence)

    def __repr__(self):
        return f"Obj of file at: {self.__path}"


if __name__ == '__main__':
    print(isnotebook())
    # load the file
    text_file = FileToProcess('data/corpuses/kawiki-latest-pages-articles_preprocessed.txt')
    text_file.load_file(max_num_of_lines=5)
    text_file.pre_process()
    text_file.save_to_file()
