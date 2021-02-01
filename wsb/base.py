# SUPER CLASSES

import pandas as pd
# import numpy as np
from datetime import datetime as dt
import pprint
from pathlib import Path
from matplotlib import pyplot as plt
from jinja2 import Template
import altair as alt

# use with caution:
# https://altair-viz.github.io/user_guide/faq.html#maxrowserror-how-can-i-plot-large-datasets
# alt.data_transformers.disable_max_rows()

# https://github.com/altair-viz/altair/issues/742
# alt.renderers.set_embed_options(theme='dark')  # only for jupyter

# alt.themes.enable("fivethirtyeight")
# alt.themes.enable("dark")


def dark_href():
    # custom theme. allows opening links in new tab
    return {
        "usermeta": {
            "embedOptions": {
                "theme": "dark",
                # loader option for opening link in new tab
                # fixed in vega-embed v6.15.1
                "loader": {"target": "_blank"}
            }
        }
    }


# register the custom theme under a chosen name
alt.themes.register('dark_href', dark_href)

# enable the newly registered theme
alt.themes.enable('dark_href')

pp = pprint.PrettyPrinter(indent=4)


class ModelBase:
    """Superclass for models.py
    PRAW Subreddit:
    https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html#praw.models.Subreddit
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
        :param sort: Can be one of: relevance, hot, top, new, comments.
                    (default: hot)
        :type sort: str
        :param search_query: search in subreddit
        :type search_query: str
        """
        self.subreddit = subreddit
        self.timefilter = timefilter
        self.limit = limit
        self.sort = sort
        self._output = output
        self.semantic_folder = f"{self._output}/semantic"
        self.search_query = search_query
        self.delim = "|"

        # should be fine to hardcode
        self.nyse_ticker_path = "./nyse-listed.csv"
        self.nyse_ticker_df = pd.read_csv(self.nyse_ticker_path)
        self.nyse_tickers = self.nyse_ticker_df["ACT Symbol"].tolist()

        self.nasdaq_ticker_path = "./nasdaq-listed.csv"
        self.nasdaq_ticker_df = pd.read_csv(self.nasdaq_ticker_path)
        self.nasdaq_tickers = self.nasdaq_ticker_df["Symbol"].tolist()

        self.words = [
            "",
            "A", "AF", "ALL", "ALLY", "AM", "AN", "ANY", "AT", "ARE", "AWAY", "ACAT",
            "AG", "AGO", "AVG", "ADX", "AI", "AA", "ADHD", "ACT", "ACH",
            "B", "BABY", "BIG", "BLUE", "BOOM",
            "C", "CALL", "CEO", "CASH", "CUZ", "CAP",
            "D", "DM", "DO", "DD", "DATA", "DE",
            "E", "ELON", "EOD", "EV", "ELSE", "EXP", "EVER", "EAT",
            "F", "FI", "FLY", "FOR", "FUEL", "FREE", "FULL", "FUND", "FCF", "FT",
            "G", "GAIN", "GAME", "GF", "GMT", "GOOD", "GS", "GOLD", "GDP",
            "H", "HAS", "HE", "HEAR", "HERO", "HF", "HOT",
            "I", "IM", "ING", "IT", "ITT", "III", "IRS", "IBKR", "IP", "IRL", "ICE",
            "JPM",
            "K",
            "L", "LINE", "LIVE", "LL", "LONG", "LOOK", "LOW", "LOAN",
            "M", "MM", "MORE", "MY", "MAN", "MAC", "MSM", "MC",
            "N", "NEWS", "NICE", "NOW", "NAME",
            "O", "ONE", "OUT", "OMG", "OI", "OCC",
            "P", "PM", "POST", "PSA", "PT", "PE", "PER", "PAY", "PPS",
            "Q",
            "R", "RH", "RE", "RBC", "RATE", "RNA",
            "S", "SC", "SHIP", "SO", "STAY", "SEE", "SAVE", "SD", "SA", "SP",
            "SOL", "SAM",
            "T", "TD", "TDA", "TIME", "TOO", "TV", "TA", "TWO", "TRUE", "TX", "TYPE",
            "USA",
            "V",
            "W", "WIN",
            "X", "XRS",
            "Y",
            "Z",
        ]

        self.tickers = [x for x in self.nyse_tickers +
                        self.nasdaq_tickers if x not in set(self.words)]
        self.ticker_cols = ["title_ticker", "submission_text_ticker"]

        self.datetime_now = dt.now()
        self.date_folder = self.datetime_now.strftime("%Y/%m/%d")
        # self.time_str = self.datetime_now.strftime("%H%M%S")

    def _get_name(self):
        """get class name
        """
        return self.__class__.__name__

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
        self._make_dir(self.semantic_folder)
        # return f"{self.semantic_folder}/{self._get_name()}.png"
        return f"{self.semantic_folder}/{self._get_name()}.json"

    def submissions(self, sort=None, comments=False):
        """get all submissions that match the attributes

        :param sort: sort type for search, optional
        :type sort: str
        :param comments: include comments, optional
        :type comments: bool
        """
        no_print_attributes = {"nyse_tickers", "nyse_ticker_df",
                               "nasdaq_tickers", "nasdaq_ticker_df",
                               "tickers", "words",
                               }
        pp.pprint(["{}: {}".format(a, getattr(self, a)) for a in vars(self)
                   if a not in no_print_attributes]
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
        return

    def merge(self, old, new):
        """replicate SQL merge

        :param old: pandas df
        :type old: obj
        :param new: pandas df:
        :type new: obj
        """
        df = old.append(new.set_index("id")
                        ).sort_values(
            ['last_updated', 'score'],
            ascending=False
        ).groupby(level=0).last()
        return df

    def save(self, df, overwrite=False):
        """save new df to file. merge if file exists

        :param df: dataframe
        :type df: pandas dataframe obj
        :param overwrite: option to set overwrite
        :type overwrite: bool
        """
        old_df = None
        # try catch for first time run. ie - curated file does not exist
        try:
            old_df = self.read_curated().set_index("id")
        except Exception as err:
            print(str(err))

        if old_df is not None and not overwrite:
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
        return

    def extract_tickers(self, df, cols=['title', 'submission_text']):
        """extract tickers from specified columns

        :param df: pandas df
        :type df: obj
        :param cols: columns to extract. DailyDiscussion will replace this with comments
        :type cols: list
        """
        # https://stackoverflow.com/questions/57483859/pandas-finding-matchany-between-list-of-strings-and-df-column-valuesas-list
        ticker_pattern = "(\$*[A-Z]{1,5})(?=[\s\.\?\!\,])+"
        # .str.join(', ').replace(r'^\s*$', np.nan, regex=True)

        cols = list(cols)
        for col in cols:
            df[f"{col}_regex"] = df[col].str.findall(ticker_pattern)
            df[f'{col}_ticker'] = [
                [val.lstrip("$")
                 for val in sublist if val.lstrip("$") in set(self.tickers)]
                for sublist in df[f'{col}_regex'].values
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
        """unused. this creates a jpg using matplotlib / pandas plot
        """
        title_df = df[["id", "title", "built_url", "title_ticker"]
                      ].drop_duplicates(subset=['id', 'title_ticker'])
        title_df["title/submission"] = "title"
        title_df = title_df.rename({"title_ticker": "ticker"}, axis=1)

        submission_df = df[["id", "title", "built_url",
                            "submission_text_ticker"]
                           ].drop_duplicates(
                               subset=['id', 'submission_text_ticker'])
        submission_df["title/submission"] = "submission"
        submission_df = submission_df.rename(
            {"submission_text_ticker": "ticker"}, axis=1)

        plot_df = self.filter_count(
            pd.concat([title_df, submission_df], ignore_index=True),
            "ticker",
            11)

        # plot here
        plot_df.groupby(["ticker", "title/submission"])["ticker"].count()\
            .unstack('title/submission').fillna(0)\
            .plot(kind='bar', stacked=True)

        plt.savefig(self.semantic_output, bbox_inches="tight")
        return

    def convert_list(self, x):
        """used to properly convert columns to list when reading csv
        """
        return x.strip("[]").split(", ")

    def clean_list_row(self, row):
        return [i.replace("'", "").replace('"', "").strip() for i in row
                if i.replace("'", "").replace('"', "").strip() not in self.words]

    def read_curated(self):
        parse_dates = ["created", "last_updated"]
        df = pd.read_csv(
            self.curated_output,
            sep=self.delim,
            parse_dates=parse_dates,
            converters={
                "title_ticker": lambda x: self.convert_list(x),
                "submission_text_ticker": lambda x: self.convert_list(x)
            }
        )

        return df

    def clean_curated(self, df=None, cols=['title_ticker', 'submission_text_ticker']):
        """altair seems to fuck up even after you filter the bad tickers
        just going to filter and overwrite the curated file

        :param df: pandas df
        :type df: obj
        :param cols: columns to clean. DailyDiscussion will replace this with comment tickers
        :type cols: list
        """
        if df is not None:
            overwrite = False
        else:
            overwrite = True
            df = self.read_curated()

        cols = list(cols)
        # https://stackoverflow.com/questions/61035426/pandas-column-containing-lists-iterate-through-each-list-problem
        for col in cols:
            df[col] = df[col].apply(
                lambda x: self.clean_list_row(x)
            )

        if overwrite:
            self.save(df, overwrite=overwrite)

        return df

    def save_semantic_chart(self, chart_json):
        with open(self.semantic_output, "w", encoding="utf-8") as f:
            f.write(chart_json)

        return

    def transform_title_submission(self, df):
        """need to explode the ticker columns because they are list type
        separate title vs submission, drop dups per df, then concat

        we don't drop dup at the end, in case we want to keep the category separation
        """
        df = self.explode(df, self.ticker_cols)

        main_cols = ["id", "title", "permalink",
                     "built_url", "score", "created"]

        title_df = df[[*main_cols, "title_ticker"]
                      ].drop_duplicates(
                          subset=['id', 'title_ticker']
        )
        title_df["title/submission"] = "title"
        title_df = title_df.rename({"title_ticker": "ticker"}, axis=1)

        submission_df = df[[*main_cols, "submission_text_ticker"]
                           ].drop_duplicates(
            subset=['id', 'submission_text_ticker']
        )
        submission_df["title/submission"] = "submission"
        submission_df = submission_df.rename(
            {"submission_text_ticker": "ticker"}, axis=1)

        plot_df = pd.concat([title_df, submission_df], ignore_index=True)
        return self.filter_count(plot_df, "ticker", 1)

    def clean_ticker(self, df):
        """clean ticker rows that are empty
        """
        # df['ticker'] = df['ticker'].str.strip()
        df = df.drop_duplicates(subset=['id', 'ticker'])
        # https://stackoverflow.com/questions/29314033/drop-rows-containing-empty-cells-from-a-pandas-dataframe
        df = df[df['ticker'].str.strip().astype(bool)]
        return df.dropna()

    def chart_title_submission(self):
        df = self.clean_ticker(
            self.transform_title_submission(
                self.read_curated()
            )
        )

        # I don't think this even fucking works but whatever. cheesed
        df = df.query("ticker not in @self.words")

        # used in data table
        df["date_str"] = df["created"].map(
            lambda x: x.strftime("%Y-%m-%d %H:%M")
        )
        # used for date filters
        df["date"] = df["created"].map(lambda x: x.strftime("%Y-%m-%d"))
        df["date2"] = df["created"].map(lambda x: x.strftime("%Y-%m-%d"))
        data_start = df["date"].min()
        data_end = df["date"].max()

        # DATETIME RANGE FILTERS
        # https://github.com/altair-viz/altair/issues/2008#issuecomment-621428053
        range_start = alt.binding(input="date")
        range_end = alt.binding(input="date")
        select_range_start = alt.selection_single(
            name="start", fields=["date"], bind=range_start,
            init={"date": data_start}
        )
        select_range_end = alt.selection_single(
            name="end", fields=["date"], bind=range_end,
            init={"date": data_end}
        )

        # slider timestamp is javascript timestamp. not human readable
        # slider = alt.binding_range(
        #     min=self.timestamp(min(self.datelist)),
        #     max=self.timestamp(max(self.datelist)),
        #     step=1, name='Created Date'
        # )
        # slider_selection = alt.selection_single(
        #     name="SelectorName", fields=['created_date'],
        #     bind=slider, init={'created': self.timestamp('2021-01-01')}
        # )

        # count slider filter
        max_count = df.groupby(["ticker"])["ticker"].count().max()
        slider_max = alt.binding_range(min=0,
                                       max=max_count,
                                       step=1)
        slider_min = alt.binding_range(min=0,
                                       max=max_count,
                                       step=1)
        select_max_count = alt.selection_single(
            name='ticker_max',
            fields=['count'],
            bind=slider_max,
            init={"count": max_count}
        )
        select_min_count = alt.selection_single(
            name='ticker_min',
            fields=['count'],
            bind=slider_min,
            init={"count": 0}
        )

        # zoom = alt.selection_interval(bind='scales')
        selector = alt.selection_single(
            empty='all',
            fields=['ticker']
        )

        base = alt.Chart(df.reset_index()).transform_filter(
            # slider_selection
            (alt.datum.date2 >= select_range_start.date) & (
                alt.datum.date2 <= select_range_end.date)
        ).add_selection(
            selector,
            select_range_start,
            select_range_end,
            select_max_count,
            select_min_count,
        )

        # BAR CHART
        # https://stackoverflow.com/questions/52385214/how-to-select-a-portion-of-data-by-a-condition-in-altair-chart
        bars = base.mark_bar().transform_aggregate(
            count='count()',
            groupby=['ticker']
        ).encode(
            x=alt.X('ticker',
                    # https://altair-viz.github.io/gallery/bar_chart_sorted.html
                    sort="-y",
                    axis=alt.Axis(title='Stock Tickers')
                    ),
            y=alt.Y("count:Q",
                    axis=alt.Axis(title='Number of Mentions'),
                    # scale=alt.Scale(zero=False)
                    ),
            color=alt.condition(selector, 'id:O', alt.value(
                'lightgray'), legend=None),
            tooltip=['ticker', 'count:Q'],
        ).properties(
            # title="Stock Ticker mentions on r/wallstreetbets",
            width=1400,
            height=400
        ).transform_filter(
            (alt.datum.count <= select_max_count.count) & (
                alt.datum.count >= select_min_count.count)
        )

        # base chart for data tables
        # href: https://altair-viz.github.io/gallery/scatter_href.html
        ranked_text = base.transform_calculate(
            url='https://www.reddit.com' + alt.datum.permalink
        ).mark_text(
            align='left',
            dx=-45,
            dy=0,
            color="white"
        ).encode(
            y=alt.Y('row_number:O', axis=None),
            href='url:N',
            tooltip=['url:N'],
            # color=alt.condition(selector,'id:O',alt.value('lightgray'),legend=None),
        ).transform_window(
            # groupby=["ticker"],  # causes overlap
            # https://altair-viz.github.io/user_guide/generated/core/altair.SortField.html#altair.SortField
            sort=[
                alt.SortField("score", "descending"),
                alt.SortField("created", "descending"),
            ],
            row_number='row_number()'
        ).transform_filter(
            selector
        ).transform_window(
            rank='rank(row_number)'
        ).transform_filter(
            # only shows up to 20 rows
            alt.datum.rank < 20
        ).properties(
            width=100,
            height=300
        )

        # Data Tables
        created = ranked_text.encode(text='date_str').properties(title='Created Date')
        ticker = ranked_text.encode(text='ticker').properties(title='Stock Ticker')
        score = ranked_text.encode(text='score').properties(title='Upvotes')
        title = ranked_text.encode(text='title').properties(title='Submission Title')
        # url = ranked_text.encode(text='built_url').properties(title='URL')

        # Combine data tables
        text = alt.hconcat(created, ticker, score, title)

        # Build final chart
        chart = alt.vconcat(
            bars,
            text,
            # autosize="fit"
        ).resolve_legend(
            color="independent"
        )

        self.save_semantic_chart(chart.to_json(indent=None))
        return


class HTMLBase:
    """separate the rendering of index.html from model.
    allows rendering of multiple models to html page.
    otherwise the html would get overwritten with only a specific model.
    """

    def __init__(self, output):
        self.last_updated = dt.now().strftime("%Y-%m-%d %H:%M")
        self._output = output
        self.semantic_folder = f"{self._output}/semantic"

        self.semantic_stock_ticker = self.read_file(f"{self.semantic_folder}/StockTicker.json")
        self.semantic_due_diligence = self.read_file(f"{self.semantic_folder}/DueDiligence.json")
        self.semantic_daily_discussion = self.read_file(f"{self.semantic_folder}/DailyDiscussion.json")

        self.html_template = Template(self.read_file("template.html"))
        self.html_output = "../index.html"

    @staticmethod
    def read_file(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as err:
            print(str(err))
            return ""

    def update_html(self):
        print("Updating index.html")
        with open(self.html_output, "w", encoding="utf-8") as f:
            # jinja2 to render
            f.write(self.html_template.render(
                vega_version=alt.VEGA_VERSION,
                vegalite_version=alt.VEGALITE_VERSION,
                # vegaembed_version=alt.VEGAEMBED_VERSION,
                vegaembed_version="6.15.1",  # hardcoding version for href _blank fix
                stock_ticker=self.semantic_stock_ticker,
                due_diligence=self.semantic_due_diligence,
                daily_discussion=self.semantic_daily_discussion,
                last_updated=self.last_updated
            ))

        return
