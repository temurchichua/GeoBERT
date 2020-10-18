import os
import string
import re
import logging

# Get the top-level logger object
log = logging.getLogger()

# make it print to the console.
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console)

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

        # Lemmatization
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
            print(f'ვიწყებ {self.file_name}-ის დამუშავებას')
        except:

        sequence = []
        prepro_sequence = []

        try:
            with open(self.path, mode='r') as text_file:
                for line in text_file:
                    line = line.strip('\n')
                    self.sequence.append(line)

        finally:
            print(f'წინადადების რაოდენობა: {len(self.sequence)}')
            text_file.close()

        if preprocess:
            self.preprocess_sequence()

    def preprocess_sequence(self):
        for element in self.sequence:
            self.prepro_sequence.append(self.preprocess_text(element))

