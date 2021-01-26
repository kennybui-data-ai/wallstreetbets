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

    def _get_name(self):
        """get class name
        """
        return self.__class__.__name__

    @property
    def raw_output(self):
        datestr = dt.now().strftime("%Y%m%d_%H%M%S")
        file_prefix = self._get_name()
        if self.search_query:
            file_prefix += "_" + self.search_query.replace(":", "_")

        return f"{self._output}/raw/{file_prefix}_{datestr}.csv"

    @property
    def curated_output(self):
        file_prefix = self._get_name()

        return f"{self._output}/curated/{file_prefix}.csv"

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
            sort = self.sort
            search_kwargs["sort"] = sort
            search_kwargs["query"] = self.search_query
        else:
            # use the other methods: hot, top, new
            search = getattr(self.subreddit, sort)
            if sort in ["new", "hot"]:
                search_kwargs.pop("time_filter")

        data = []
        for submission in search(**search_kwargs):
            # https://praw.readthedocs.io/en/latest/code_overview/models/submission.html#praw.models.Submission
            row = {
                "id": submission.id,
                "title": submission.title,
                "name": submission.name,
                "upvote_ratio": submission.upvote_ratio,
                "ups": submission.ups,
                "score": submission.score,
                "sort": sort,
                "created": dt.fromtimestamp(submission.created),  # .strftime('%c'),  # epoch
                "author": submission.author,
                "num_comments": submission.num_comments,
                "flair": submission.link_flair_text,
                "permalink": submission.permalink,
                "built_url": f"https://www.reddit.com{submission.permalink}",
                "url": submission.url,
                "submission_test": submission.selftext,
                "last_updated": dt.now(),
                "raw_filename": self.raw_output,
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
        self._raw_save(df)
        return df

    def _raw_save(self, df):
        """save raw submissions pandas dataframe

        :param df: dataframe
        :type df: pandas dataframe obj
        """
        df.to_csv(
            self.raw_output,
            # sep="|"
        )

    def save(self, df):
        """merge curated pandas dataframe to existing curated file

        :param df: dataframe
        :type df: pandas dataframe obj
        """
        old_df = None
        try:
            parse_dates = ["created", "last_updated"]
            old_df = pd.read_csv(self.curated_output, parse_dates=parse_dates).set_index("id")
        except Exception as err:
            print(str(err))

        if old_df is not None:
            curated_df = old_df.append(df.set_index("id")).sort_values('last_updated').groupby(level=0).last()
        else:
            curated_df = df

        # with open(self.curated_output, "w") as f:
        curated_df.to_csv(
            # f,
            self.curated_output,
            # sep="|"
        )
