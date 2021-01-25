import praw
import models
import argparse
from datetime import datetime


class MoneyPrinter:
    """BRRRRRRRRRRRRRRRRR
    """

    def __init__(self):
        """init the print
        """
        pass

    def pump(self):
        """ extract posts
        """
        pass

    def tendies(self):
        """ mine the posts using the models
        """
        pass

    def go_brrr(self):
        """ pump out them tendies
        """
        print("BRRRRRR")
        pass


def parse_args():
    """function for command line args
    TODO
    """
    parser = argparse.ArgumentParser(
        description='Money Printer Go BRRR')
    parser.add_argument('-sd', '--startdate', type=str, default=datetime.today().strftime('%Y%m%d'),
                        help='YYYYMMDD. Default is datetime.today()')
    parser.add_argument('-t', '--ticker', action='store_true',
                        help='Ticker model. Default is False')
    parser.add_argument('-dd', '--dailydiscussion', action='store_true',
                        help='Daily Discussion model. Default is False')
    # parser.add_argument('--fresh', action='store_true',
    #                     help='Regenerate (ie - delete and create) fresh 3_output scripts. Default is False')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')

    return parser.parse_args()

# if __name__ == "__main__":
#     args = parse_args()
#     for arg in vars(args):
#         print arg, getattr(args, arg)

#     mp = MoneyPrinter()
#     mp.go_brrr()

reddit = praw.Reddit(client_id="CLIENT_ID", client_secret="CLIENT_SECRET",
                     password="PASSWORD", user_agent="USERAGENT",
                     username="USERNAME")
reddit.subreddit("r/wallstreetbets")
