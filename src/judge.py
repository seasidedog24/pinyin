import os
import logging
from .const import DAT_DIR


def check(std_file, output_list):
    with open(std_file, "r", encoding="utf-8") as f:
        std_lines = [line.strip() for line in f if line.strip()]
    total_word = 0
    correct_word = 0
    total_sentence = 0
    correct_sentence = 0

    for line, std_line in zip(output_list, std_lines):
        line = line.strip()
        if not line:
            continue
        total_word += len(line)
        correct_word += sum(a == b for a, b in zip(line, std_line))
        correct_sentence += (line == std_line)
        total_sentence += 1

    word_accuracy = correct_word / total_word if total_word else 0
    sentence_accuracy = correct_sentence / total_sentence if total_sentence else 0
    return word_accuracy, sentence_accuracy


def judge(output_list):
    std_file = os.path.join(DAT_DIR, "answer.txt")

    try:
        word_accuracy_rate, sentence_accuracy_rate = check(
            std_file, output_list)
        logging.info('─' * 50)
        logging.info('Evaluation Results:')
        logging.info('Word Accuracy:     {:.2f}%'.format(
            word_accuracy_rate * 100))
        logging.info('Sentence Accuracy: {:.2f}%'.format(
            sentence_accuracy_rate * 100))
        logging.info('─' * 50)

        word_accuracy_rate_str = "{:.2f}".format(word_accuracy_rate * 100)
        sentence_accuracy_rate_str = "{:.2f}".format(
            sentence_accuracy_rate * 100)
        return word_accuracy_rate_str, sentence_accuracy_rate_str
        
    except Exception as e:
        logging.error("✗ Cannot calculate accuracy: {}".format(e))
        return "0.00", "0.00"


if __name__ == "__main__":
    output_file = os.path.join(DAT_DIR, "output.txt")
    with open(output_file, "r", encoding="utf-8") as f:
        output_list = f.readlines()
        judge(output_list)
