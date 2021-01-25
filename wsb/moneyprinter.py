import praw
# import sys
import models
import argparse
from datetime import datetime
import json


class MoneyPrinter:
    """BRRRRRRRRRRRRRRRRR
    """

    def __init__(self, credentials_path):
        """init the print

        :param credentials_path: path to OAuth2.0 credentials for Reddit API
        :type credentials_path: str
        """
        with open(credentials_path, "r") as f:
            self.credentials = json.loads(f.read())

        self.reddit = praw.Reddit(client_id=self.credentials["client_id"],
                                  client_secret=self.credentials["client_secret"],
                                  refresh_token=self.credentials["refresh_token"],
                                  user_agent=self.credentials["user_agent"]
                                  )
        self.subreddit = self.reddit.subreddit("wallstreetbets")
        self.dailydiscussion = models.DailyDiscussion(self.subreddit)
        self.ticker = models.Ticker(self.subreddit)

    def pump(self):
        """test
        """
        print(self.subreddit.display_name)
        print(self.subreddit.title)
        print(self.subreddit.description)
        for submission in self.subreddit.hot(limit=10):
            print(submission.title)
            print(submission.score)
            print(submission.id)
            print(submission.url)

    def go_brrr(self, args):
        """ pump out them tendies

        :param args: cmdline args
        :type args: argparse obj
        """
        self.pump()

        if args.dailydiscussion:
            self.dailydiscussion.tendies()

        if args.ticker:
            self.ticker.tendies()

        print("BRRRRRR")


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


if __name__ == "__main__":
    args = parse_args()
    for arg in vars(args):
        print(arg, getattr(args, arg))

    credentials_path = "./credentials.json"
    mp = MoneyPrinter(credentials_path)
    mp.go_brrr(args)
