# Imports
import os
import subprocess
from sys import platform

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
def is_notebook():
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


def file_path(file_name, clear=False):
    """generates abs path relative to the Package and modules"""
    # If running from notebook
    if is_notebook():
        cwd = os.getcwd()
        f_path = cwd + file_name
    else:
        data_dir = os.path.abspath('')
        f_path = os.path.join(data_dir, file_name)

    # if file needs to be cleaned
    if clear:
        clear_file(f_path)
    # check if the path exists
    if os.path.exists(f_path):
        return f_path
    else:
        raise FileNotFoundError


def clear_file(f_path):
    file_to_clear = open(f_path, 'w')
    file_to_clear.write('')
    file_to_clear.close()


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


def lines_in_file(f_path):
    if platform == "linux" or platform == "linux2":
        result = int(subprocess.check_output(['wc', '-l', f_path]).split()[0])

    elif platform == "win32":
        try:
            with open(f_path) as f:
                result = sum(1 for _ in tqdm(f, desc=f"Count for {f_path}"))
        except:
            result = 0

    return result


numbers = set("0123456789")
symbols = set("!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c")
letters = set('ქწერტყუიოპჭღთასდფგჰჯკლშჟ₾ზხცვბნმძჩ')
printable = set().union(*[numbers, symbols, letters])


class FileToProcess():
    def __init__(self, file_name=None, stop_words="data/stops.txt", save_file=None, append=False):

        if not file_name:
            raise ValueError("Init FileToProcess class with path to the file as file_name argument ")

        self.file_name = file_name
        self.__read_path = file_path(file_name)
        self.__status = os.stat(self.__read_path)

        if not save_file:
            save_file = f"{self.file_name.split('.')[0]}_pre_processed.txt"

        self.save_file = save_file
        self.__save_path = file_path(self.save_file, clear=not append)

        self.stop_words = set(line.strip() for line in open(file_path(stop_words), encoding='utf-8'))
        self.number_of_lines = lines_in_file(self.__read_path)

    def preprocess_and_append(self, max_num_of_lines=-1):

        # Progress bar
        pool = mp.Pool(SUBS)
        n = 0
        with pool:
            description = f"Processing the file: {self.file_name}"
            total = self.number_of_lines
            with open(self.__read_path, mode='r', encoding='utf-8') as file:
                pool_to_iter = pool.imap_unordered(self._check_and_update,
                                                   open(self.__read_path, mode='r', encoding='utf-8'))

            pbar = tqdm(pool_to_iter, desc=description, total=total)

            for _ in pbar:

                if n == max_num_of_lines:
                    break
                n += 1

        # Finally:
        log.info(f'To file: {lines_in_file(self.__save_path)} | {sizeof_fmt(os.stat(self.__save_path).st_size)}')
        log.info(f'Saved number of lines: {lines_in_file(self.__save_path)}')

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

        index_range = range(len(tokens) - 1, -1, -1)
        for index in index_range:
            word = tokens[index]
            if len(word) < min_word_size or len(word) > max_word_size \
                    or is_not_printable(word) or word in self.stop_words:
                tokens.pop(index)

        if len(tokens) < min_sentence_size:
            return None

        preprocessed_text = ' '.join(tokens)

        return preprocessed_text

    def _check_and_update(self, sentence):
        sentence = fix_encoding(sentence)
        if pre_processed_sentence := self.__preprocess_text(sentence):
            # log.info(f"replaceing: {sentence} > {pre_processed_sentence}")
            self.save_to_file(pre_processed_sentence)

    def save_to_file(self, sentence):

        with open(self.__save_path, 'a', encoding="utf-8") as output:
            # Progress bar
            output.write(str(sentence) + '\n')

    def __len__(self):
        return self.number_of_lines

    def __repr__(self):
        return f"Obj of file at: {self.__read_path}"


if __name__ == '__main__':
    print(is_notebook())
    # load the file
    text_file = FileToProcess('data/corpuses/kawiki-latest-pages-articles_preprocessed.txt',
                              save_file='data/corpuses/pre_processed.txt')
    text_file.preprocess_and_append(max_num_of_lines=5)
