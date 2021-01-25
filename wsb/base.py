# superclasses

import pandas as pd
from datetime import datetime as dt
import pprint

pp = pprint.PrettyPrinter(indent=4)


class ModelBase:
    """Superclass for models.py
    PRAW Subreddit: https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html#praw.models.Subreddit
    """

    def __init__(self, subreddit, timefilter, limit, output,
                 sort="hot", search_query=None):
        """init

        :param subreddit: subreddit client
        :type subreddit: reddit.subreddit obj
        :param timefilter: day, week, month, year
        :type timefilter: str
        :param limit: number of submissions to extract
        :type limit: int
        :param output: output folder
        :type output: str
        :param sort: Can be one of: relevance, hot, top, new, comments. (default: hot)
        :type sort: str
        :param search_query: search in subreddit
        :type search_query: str
        """
        self.subreddit = subreddit
        self.timefilter = timefilter
        self.limit = limit
        self.sort = sort
        self._output = output
        self.search_query = search_query

    @property
    def output(self):
        datestr = dt.now().strftime("%Y%m%d_%H%M%S")
        file_prefix = self.search_query.replace(":", "_")
        return f"{self._output}/{file_prefix}_{datestr}.csv"

    def submissions(self, sort=None, comments=False):
        """get all submissions that match the attributes

        :param sort: sort type for search, optional
        :type sort: str
        :param comments: include comments, optional
        :type comments: bool
        """
        pp.pprint(["{}: {}".format(a, getattr(self, a)) for a in vars(self)]
                  )

        # https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html?highlight=subreddit#praw.models.Subreddit.search
        search_kwargs = {
            "time_filter": self.timefilter,
            "limit": self.limit
        }
        if self.search_query:
            search = self.subreddit.search
            search_kwargs["sort"] = self.sort
            search_kwargs["query"] = self.search_query
        else:
            # would be one of the other methods: hot, top, new
            search = getattr(self.subreddit, sort)
            if sort in ["new", "hot"]:
                search_kwargs.pop("time_filter")

        data = []
        for submission in search(**search_kwargs):
            row = {
                "title": submission.title,
                "upvote_ratio": submission.upvote_ratio,
                "ups": submission.ups,
                "score": submission.score,
                "created": dt.fromtimestamp(submission.created).strftime('%c'),  # epoch
                "author": submission.author,
                "num_comments": submission.num_comments,
                "permalink": submission.permalink,
                "built_url": f"https://www.reddit.com{submission.permalink}",
                "submission_test": submission.selftext,
            }

            if comments:
                # https://praw.readthedocs.io/en/latest/tutorials/comments.html#extracting-comments
                # TODO post processing, maybe let models take care of that
                # fyi this takes quite a few seconds
                submission.comments.replace_more(limit=None)  # setting limit will iterate through less comments
                row["comments"] = [comment.body for comment in submission.comments.list()]

            # for col in vars(submission):
            #     row[col] = getattr(submission, col)

            # print(row)
            data.append(row)

        df = pd.DataFrame(data)
        return df, self.output
