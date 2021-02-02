import praw
import models
import argparse
import json
from timeit import default_timer as timer
import humanize


class MoneyPrinter:
    """BRRRRRRRRRRRRRRRRR
    """

    def __init__(self, args):
        """init the print
        :param args: cmdline args
        :type args: argparse obj
        """
        with open(args.credentials, "r") as f:
            self.credentials = json.loads(f.read())

        self.reddit = praw.Reddit(client_id=self.credentials["client_id"],
                                  client_secret=self.credentials["client_secret"],
                                  refresh_token=self.credentials["refresh_token"],
                                  user_agent=self.credentials["user_agent"]
                                  )
        self.subreddit = self.reddit.subreddit("wallstreetbets")
        self.timefilter = args.timefilter
        self.output = args.output
        self.limit = args.limit

        not_models = {"timefilter", "output", "credentials", "limit", "all"}
        if args.all:
            self.modelnames = [a for a in vars(args) if a not in not_models]
        else:
            self.modelnames = [a for a in vars(args) if a not in not_models and getattr(args, a)]

    def pump(self):
        """test
        """
        print("""
Welcome to
              /$$                       /$$ /$$             /$$                                     /$$     /$$                   /$$             
             /$$/                      | $$| $$            | $$                                    | $$    | $$                  | $$             
  /$$$$$$   /$$//$$  /$$  /$$  /$$$$$$ | $$| $$  /$$$$$$$ /$$$$$$    /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$  /$$$$$$   /$$$$$$$
 /$$__  $$ /$$/| $$ | $$ | $$ |____  $$| $$| $$ /$$_____/|_  $$_/   /$$__  $$ /$$__  $$ /$$__  $$|_  $$_/  | $$__  $$ /$$__  $$|_  $$_/  /$$_____/
| $$  \__//$$/ | $$ | $$ | $$  /$$$$$$$| $$| $$|  $$$$$$   | $$    | $$  \__/| $$$$$$$$| $$$$$$$$  | $$    | $$  \ $$| $$$$$$$$  | $$   |  $$$$$$ 
| $$     /$$/  | $$ | $$ | $$ /$$__  $$| $$| $$ \____  $$  | $$ /$$| $$      | $$_____/| $$_____/  | $$ /$$| $$  | $$| $$_____/  | $$ /$$\____  $$
| $$    /$$/   |  $$$$$/$$$$/|  $$$$$$$| $$| $$ /$$$$$$$/  |  $$$$/| $$      |  $$$$$$$|  $$$$$$$  |  $$$$/| $$$$$$$/|  $$$$$$$  |  $$$$//$$$$$$$/
|__/   |__/     \_____/\___/  \_______/|__/|__/|_______/    \___/  |__/       \_______/ \_______/   \___/  |_______/  \_______/   \___/ |_______/   version 0.0.1
    """)
        # print(self.subreddit.display_name)
        # print(self.subreddit.title)
        # print(self.subreddit.description)
        # for submission in self.subreddit.hot(limit=10):
        #     print("####################")
        #     print(submission.title)
        #     print(submission.score)
        #     print(submission.id)
        #     print(submission.url)

    def go_brrr(self):
        """ pump out them tendies
        """
        self.pump()

        # dynamically pull the models based on modelnames
        for m in self.modelnames:
            model = getattr(models, m)(
                subreddit=self.subreddit,
                timefilter=self.timefilter,
                limit=self.limit,
                output=self.output
            )
            # tendies is main method of model
            model.tendies()

        models.HTML(self.output).tendies()

        print("BRRRRRR")


def parse_args():
    """function for command line args
    TODO
    """
    # optional custom configuration
    parser = argparse.ArgumentParser(description='Money Printer Go BRRRRRRR')
    parser.add_argument('-c', '--credentials', type=str, default="./credentials.json",
                        help='Credentials file. Default is ./credentials.json')
    parser.add_argument('-t', '--timefilter', type=str, default="day",
                        help='Choose time filter for Reddit search query. Only used for top and search methods. Default is day',
                        choices=["all", "day", "hour", "month", "week", "year"])
    parser.add_argument('-l', '--limit', type=int, default=None,
                        help="""Number of posts returned from Reddit search query. If limit is None, then fetch as many entries as possible.
                        Most of reddit’s listings contain a maximum of 1000 items, and are returned 100 at a time. Default is None""")
    parser.add_argument('-o', '--output', type=str, default="../output",
                        help='output folder for model. Default is ../output')

    # enable models.py
    parser.add_argument('--all', action='store_true', help='Runs all models. Overrides the model flags. Default is False')
    parser.add_argument('-st', '--stockticker', action='store_true', dest="StockTicker",
                        help='Stock Ticker search. Default is False')
    parser.add_argument('-dd', '--duediligence', action='store_true', dest="DueDiligence",
                        help='Due Diligence flair. Default is False')
    parser.add_argument('-d', '--dailydiscussion', action='store_true', dest="DailyDiscussion",
                        help='Daily Discussion flair. Default is False')

    # parser.add_argument('--fresh', action='store_true',
    #                     help='Regenerate (ie - delete and create) fresh 3_output scripts. Default is False')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')

    return parser.parse_args()


if __name__ == "__main__":
    start = timer()
    args = parse_args()
    mp = MoneyPrinter(args)
    try:
        mp.go_brrr()
    except KeyboardInterrupt:
        print("[CTRL+C detected]")
    finally:
        end = timer()

        print("Total execution time:", humanize.naturaldelta(end-start))
