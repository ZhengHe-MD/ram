import logging
import sys

from ram import execute

if __name__ == "__main__":
    # init logging
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

    execute()
