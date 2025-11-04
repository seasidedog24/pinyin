import argparse
import sys
from src import predict, train, judge
from src.train import metric
import logging


@metric
def process_input(args):
    output_list = []
    for line in sys.stdin:
        pinyin_text = line.strip()
        result = predict.predict(pinyin_text, args.alpha)
        print(result)
        output_list.append(result)

    judge.judge(output_list)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--alpha", type=float, default=1e-7,
                        help="Alpha parameter for 2-gram model")

    args = parser.parse_args()

    train.train()
    process_input(args)


if __name__ == "__main__":
    main()
