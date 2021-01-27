# superclasses

import pandas as pd
import numpy as np
from datetime import datetime as dt
import pprint
from pathlib import Path
from matplotlib import pyplot as plt
from highcharts import Highchart
# from ast import literal_eval

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
        self.delim = "|"

        # should be fine to hardcode
        self.nyse_ticker_path = "./nyse-listed.csv"
        self.nyse_ticker_df = pd.read_csv(self.nyse_ticker_path)
        self.nyse_tickers = self.nyse_ticker_df["ACT Symbol"].tolist()

        self.nasdaq_ticker_path = "./nasdaq-listed.csv"
        self.nasdaq_ticker_df = pd.read_csv(self.nasdaq_ticker_path)
        self.nasdaq_tickers = self.nasdaq_ticker_df["Symbol"].tolist()

        self.tickers = self.nyse_tickers + self.nasdaq_tickers
        self.ticker_cols = ["title_ticker", "submission_text_ticker"]

        self.datetime_now = dt.now()
        self.date_folder = self.datetime_now.strftime("%Y/%m/%d")
        # self.time_str = self.datetime_now.strftime("%H%M%S")

    def _get_name(self):
        """get class name
        """
        return self.__class__.__name__

    @property
    def highchart(self):
        return Highchart(width=850, height=600)

    @staticmethod
    def _make_dir(folder):
        """make the directory
        """
        try:
            Path(folder).mkdir(parents=True, exist_ok=True)
        except Exception as err:
            print(str(err))

        return

    @property
    def raw_output(self):
        file_prefix = self._get_name()
        if self.search_query:
            file_prefix += "_" + self.search_query.replace(":", "_")

        folder = f"{self._output}/raw/{self.date_folder}"
        self._make_dir(folder)
        time_str = dt.now().strftime("%H%M%S")
        return f"{folder}/{file_prefix}_{time_str}.csv"

    @property
    def curated_output(self):
        return f"{self._output}/curated/{self._get_name()}.csv"

    @property
    def semantic_output(self):
        return f"{self._output}/semantic/{self._get_name()}.png"

    def submissions(self, sort=None, comments=False):
        """get all submissions that match the attributes

        :param sort: sort type for search, optional
        :type sort: str
        :param comments: include comments, optional
        :type comments: bool
        """
        no_print_attributes = {"nyse_tickers", "nyse_ticker_df",
                               "nasdaq_tickers", "nasdaq_ticker_df", "tickers"}
        pp.pprint(["{}: {}".format(a, getattr(self, a)) for a in vars(self) if a not in no_print_attributes]
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
                # .strftime('%c'),  # epoch
                "created": dt.fromtimestamp(submission.created),
                "author": submission.author,
                "num_comments": submission.num_comments,
                "flair": submission.link_flair_text,
                "permalink": submission.permalink,
                "built_url": f"https://www.reddit.com{submission.permalink}",
                "url": submission.url,
                "submission_text": submission.selftext,
                "last_updated": self.datetime_now,
                "raw_filename": self.raw_output,
                "model": self._get_name(),
            }

            if comments:
                # https://praw.readthedocs.io/en/latest/tutorials/comments.html#extracting-comments
                # TODO post processing, maybe let models take care of that
                # fyi this takes quite a few seconds
                # setting limit will iterate through less comments
                submission.comments.replace_more(limit=None)
                row["comments"] = [
                    comment.body for comment in submission.comments.list()]

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
            self.delim
        )

    def merge(self, old, new):
        """replicate SQL merge

        :param old: pandas df
        :type old: obj
        :param new: pandas df:
        :type new: obj
        """
        df = old.append(new.set_index("id"))\
            .sort_values(['last_updated', 'score'], ascending=False)\
            .groupby(level=0).last()
        return df

    def save(self, df):
        """save new df to existing file

        :param df: dataframe
        :type df: pandas dataframe obj
        """
        old_df = None
        # try catch for first time run. ie - curated file does not exist
        try:
            parse_dates = ["created", "last_updated"]
            old_df = pd.read_csv(self.curated_output,
                                 parse_dates=parse_dates,
                                 sep=self.delim)\
                .set_index("id")
        except Exception as err:
            print(str(err))

        if old_df is not None:
            df = self.merge(
                old=old_df,
                new=df
            )
        else:
            pass

        df.to_csv(
            self.curated_output,
            sep=self.delim
        )

    def extract_tickers(self, df):
        # https://stackoverflow.com/questions/57483859/pandas-finding-matchany-between-list-of-strings-and-df-column-valuesas-list
        ticker_pattern = "(\$*[A-Z]{1,5})(?=[\s\.\?\!\,])+"
        # .str.join(', ').replace(r'^\s*$', np.nan, regex=True)
        df["title_regex"] = df['title'].str.findall(ticker_pattern)
        df['title_ticker'] = [
            [val.lstrip("$")
             for val in sublist if val.lstrip("$") in self.tickers]
            for sublist in df['title_regex'].values
        ]

        df['submission_text_regex'] = df['submission_text'].str.findall(
            ticker_pattern)
        df['submission_text_ticker'] = [
            [val.lstrip("$")
             for val in sublist if val.lstrip("$") in self.tickers]
            for sublist in df['submission_text_regex'].values
        ]

        return df

    @staticmethod
    def explode(df, cols):
        """method to explode list columns. mainly used for stock ticker columns

        :param df: pandas df
        :type df: obj
        :param cols: list of cols to explode
        :type cols: list
        """
        for col in cols:
            df = df.explode(col)

        return df

    @staticmethod
    def filter_count(df, col, min):
        return df[df.groupby(col)[col].transform('count') > min]

    def plot_tickers(self, df):
        title_df = df[["id", "title", "built_url", "title_ticker"]].drop_duplicates(
            subset=['id', 'title_ticker'])
        title_df["title/submission"] = "title"
        title_df = title_df.rename({"title_ticker": "ticker"}, axis=1)

        submission_df = df[["id", "title", "built_url", "submission_text_ticker"]].drop_duplicates(
            subset=['id', 'submission_text_ticker'])
        submission_df["title/submission"] = "submission"
        submission_df = submission_df.rename(
            {"submission_text_ticker": "ticker"}, axis=1)

        plot_df = self.filter_count(
            pd.concat([title_df, submission_df], ignore_index=True),
            "ticker",
            11)

        # plot here
        plot_df.groupby(["ticker", "title/submission"])["ticker"].count().unstack('title/submission').fillna(0)\
            .plot(kind='bar', stacked=True)

        plt.savefig(self.semantic_output, bbox_inches="tight")

        def convert_list(self, x):
            return x.strip("[]").split(", ")
