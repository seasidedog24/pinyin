import json
import os
import time
import logging
from tqdm import tqdm
from glob import glob
from .const import COR_DIR, RES_DIR, SRC_DIR


def metric(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        func_name = func.__name__.replace('_', ' ').title()
        logging.info('✓ {} completed in {:.2f}s'.format(func_name, end - start))
        return result
    return wrapper


# frequency of word
freq_one_py = {}
freq_one_word = {}
freq_two_word = {}

# probability of word
prob_one_word = {}
# conditional probability of word in 2-gram model
prob_two_word = {}

IS_TRAINED = False


def freq_stat_line(freq_1_word, freq_2_word, word_list, line):
    line = line.strip()
    if len(line) == 0:
        return
    last_word = "#"
    for word in line:
        if word not in word_list:
            last_word = "#"
            continue
        # count 1-word frequency
        freq_1_word[word] = freq_1_word.get(word, 0) + 1

        # count 2-word frequency
        if last_word != "#":
            word_pair = last_word + word
            freq_2_word[word_pair] = freq_2_word.get(word_pair, 0) + 1

        last_word = word


def process_single_file(file_name, freq_one_word, freq_two_word, word_list):
    new_freq_one_word = {}
    new_freq_two_word = {}
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            for line in tqdm(f.readlines(), desc="Processing file...", leave=False):
                freq_stat_line(new_freq_one_word,
                               new_freq_two_word, word_list, line)
    except UnicodeDecodeError:
        new_freq_one_word = {}
        new_freq_two_word = {}
        with open(file_name, "r", encoding="gbk") as f:
            for line in tqdm(f.readlines(), desc="Processing file...", leave=False):
                freq_stat_line(new_freq_one_word,
                               new_freq_two_word, word_list, line)

    for word, count in new_freq_one_word.items():
        freq_one_word[word] = freq_one_word.get(word, 0) + count

    for word_pair, count in new_freq_two_word.items():
        freq_two_word[word_pair] = freq_two_word.get(word_pair, 0) + count

    return freq_one_word, freq_two_word


def get_word_list():
    pinyin2word = {}
    word_list = []
    word2pinyin = {}

    with open(os.path.join(SRC_DIR, 'alphabet', '拼音汉字表.txt'), "r", encoding="gbk") as f:
        for line in f.readlines():
            data = line.split()
            pinyin2word[data[0]] = data[1:]

    with open(os.path.join(SRC_DIR, 'alphabet', '一二级汉字表.txt'), "r", encoding="gbk") as f:
        data = f.read()
        word_list = list(data)

    for pinyin, words in pinyin2word.items():
        for word in words:
            if word not in word2pinyin:
                word2pinyin[word] = [pinyin]
            else:
                word2pinyin[word].append(pinyin)

    # check if the word list is consistent with the pinyin list
    assert (all([word in word2pinyin for word in word_list]))
    assert (all([word in word_list for word in word2pinyin]))

    return pinyin2word, word2pinyin


@metric
def process_files():
    pinyin2word, word2pinyin = get_word_list()

    word_list = set(word2pinyin.keys())

    file_list = [filename for filename in glob(os.path.join(
        COR_DIR, "**/*"), recursive=True) if os.path.isfile(filename)]

    freq_one_word = {}
    freq_two_word = {}

    with tqdm(total=len(file_list), desc="Generating 2-word table...", leave=True) as pbar:
        for file in file_list:
            pbar.set_description(
                f"Generating 2-word table, processing file: {file}")
            freq_one_word, freq_two_word = process_single_file(
                file, freq_one_word, freq_two_word, word_list)
            pbar.update(1)

    return pinyin2word, freq_one_word, freq_two_word


@metric
def dump_json(freq_one_word, freq_two_word):
    with open(os.path.join(RES_DIR, "one_word.json"), "w", encoding="utf-8") as f:
        json.dump(freq_one_word, f, ensure_ascii=False)

    with open(os.path.join(RES_DIR, "two_word.json"), "w", encoding="utf-8") as f:
        json.dump(freq_two_word, f, ensure_ascii=False)


@metric
def load_json():
    with open(os.path.join(RES_DIR, "one_word.json"), "r", encoding="utf-8") as f:
        freq_one_word = json.load(f)

    with open(os.path.join(RES_DIR, "two_word.json"), "r", encoding="utf-8") as f:
        freq_two_word = json.load(f)

    return freq_one_word, freq_two_word


def train():
    global IS_TRAINED, freq_one_word, freq_two_word, prob_one_word, prob_two_word
    try:
        freq_one_word, freq_two_word = load_json()
        pinyin2word, _ = get_word_list()
    except FileNotFoundError or json.decoder.JSONDecodeError:
        pinyin2word, freq_one_word, freq_two_word = process_files()
        dump_json(freq_one_word, freq_two_word)

    prob_one_word, prob_two_word = calculate_probability(pinyin2word,
                                                          freq_one_word, freq_two_word)
    IS_TRAINED = True


def calculate_probability(pinyin2word, one_word, two_word):
    prob_one_word = {}
    for pinyin, words in pinyin2word.items():
        prob_one_word[pinyin] = {}
        total = 0
        for word in words:
            total += one_word.get(word, 0) + 1
        for word in words:
            prob_one_word[pinyin][word] = (one_word.get(word, 0) + 1) / total

    prob_two_word = {}
    for word_pair in two_word:
        prob_two_word[word_pair] = two_word[word_pair] / one_word[word_pair[0]]

    return prob_one_word, prob_two_word
