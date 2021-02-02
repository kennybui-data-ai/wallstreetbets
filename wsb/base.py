# SUPER CLASSES

import pandas as pd
# import numpy as np
from datetime import datetime as dt
import pprint
from pathlib import Path
from matplotlib import pyplot as plt
from jinja2 import Template
import altair as alt
from ast import literal_eval

# use with caution:
# https://altair-viz.github.io/user_guide/faq.html#maxrowserror-how-can-i-plot-large-datasets
alt.data_transformers.disable_max_rows()

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
                 sort="hot", search_query=None,
                 cols_with_ticker=["title", "submission_text"]):
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
        :param cols_with_ticker: columns with ticker. used for explode, extract, clean
        :type cols_with_ticker: list
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
            "C", "CALL", "CEO", "CASH", "CUZ", "CAP", "CA",
            "D", "DM", "DO", "DD", "DATA", "DE",
            "E", "ELON", "EOD", "EV", "ELSE", "EXP", "EVER", "EAT", "EYES",
            # "F",  # this is Ford
            "FI", "FLY", "FOR", "FUEL", "FREE", "FULL", "FUND", "FCF", "FT",
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
            "R", "RE", "RBC", "RATE", "RNA",
            # "RH",  # this is Robinhood trading app
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
        self.cols_with_ticker = list(cols_with_ticker)
        self.ticker_cols = [f"{col}_ticker" for col in self.cols_with_ticker]

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
            file_prefix += "_" + self.search_query.replace(":", "_").replace('"', "")

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
        pp.pprint(
            {
                "subreddit": self.subreddit.display_name,
                "timefilter": self.timefilter,
                "limit": self.limit,
                "sort": self.sort,
                "search_query": self.search_query,
                "cols_with_ticker": self.cols_with_ticker,
                "ticker_cols": self.ticker_cols,
            }
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
            # use the other methods: hot, top, new, controversial
            search = getattr(self.subreddit, sort)
            if sort in ["new", "hot"]:
                search_kwargs.pop("time_filter")

        data = []
        for submission in search(**search_kwargs):
            # https://praw.readthedocs.io/en/latest/code_overview/models/submission.html#praw.models.Submission
            if comments:
                # https://praw.readthedocs.io/en/latest/tutorials/comments.html
                print("====================")
                print("getting comments")

                # https://praw.readthedocs.io/en/latest/tutorials/comments.html#the-replace-more-method
                # replace_more(limit=None) is infinite top level comments.
                # leave as default 32 cuz it's SUPEERRRR slow.
                submission.comments.replace_more()
                max_length = len(submission.comments.list())
                # i = 1
                print(f"number of comments in submission: {max_length}")
                print("extracting comments now")

                # submission.comments.list() gives the entire comment forest
                for comment in submission.comments.list():
                    # print(f"{i} in {max_length}")
                    # i += 1
                    # print(vars(comment))
                    row = {
                        "id": comment.id,
                        "author": comment.author,
                        # "title": submission.title,
                        "total_awards_received": comment.total_awards_received,
                        "downs": comment.downs,
                        "ups": comment.ups,
                        "score": comment.score,
                        "comment": comment.body,
                        "created": dt.fromtimestamp(comment.created_utc),
                        "permalink": comment.permalink,
                        "built_url":  f"https://www.reddit.com{comment.permalink}",
                        "sort": sort,
                        "last_updated": self.datetime_now,
                        "raw_filename": self.raw_output,
                        "model": self._get_name(),
                    }
                    data.append(row)
            else:
                row = {
                    "id": submission.id,
                    "title": submission.title,
                    "name": submission.name,
                    "upvote_ratio": submission.upvote_ratio,
                    "ups": submission.ups,
                    "score": submission.score,
                    "sort": sort,
                    "created": dt.fromtimestamp(submission.created_utc),  # .strftime('%c'),  # epoch
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
        """save df to curated file. merge if file exists

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

    def extract_tickers(self, df):
        """extract tickers from columns with ticker

        :param df: pandas df
        :type df: obj
        """
        # https://stackoverflow.com/questions/57483859/pandas-finding-matchany-between-list-of-strings-and-df-column-valuesas-list
        ticker_pattern = "(\$*[A-Z]{1,5})(?=[\s\.\?\!\,])+"
        # .str.join(', ').replace(r'^\s*$', np.nan, regex=True)

        for col in self.cols_with_ticker:
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
        """UNUSED. this creates a jpg using matplotlib / pandas plot
        """
        plot_df = self.transform(df, min_count=11)

        # agg, unstack and plot
        self.clean(
            plot_df.groupby(["ticker", "category"])["ticker"].count()
            .unstack('category')
        ).fillna(0).plot(kind='bar', stacked=True)

        plt.savefig(self.semantic_output, bbox_inches="tight")
        return

    def read_curated(self):
        converters = {}
        for col in self.ticker_cols:
            converters[col] = literal_eval

        parse_dates = ["created", "last_updated"]
        df = pd.read_csv(
            self.curated_output,
            sep=self.delim,
            parse_dates=parse_dates,
            converters=converters
        )

        return df

    def clean_curated(self, df=None):
        """altair seems to fuck up even after you filter the bad tickers
        just going to filter and overwrite the curated file

        :param df: pandas df
        :type df: obj
        """
        if df is not None:
            overwrite = False
        else:
            overwrite = True
            df = self.read_curated()

        # https://stackoverflow.com/questions/61035426/pandas-column-containing-lists-iterate-through-each-list-problem
        for col in self.ticker_cols:
            df[col] = df[col].apply(
                lambda x: [
                    i.replace("'", "").replace('"', "").strip() for i in x
                    if i.replace("'", "").replace('"', "").strip() not in self.words
                ]
            )

        if overwrite:
            self.save(df, overwrite=overwrite)

        return df

    def save_semantic_chart(self, chart_json):
        with open(self.semantic_output, "w", encoding="utf-8") as f:
            f.write(chart_json)

        return

    def transform(self, df, min_count=1):
        """need to explode the ticker columns because they are list type
        we don't drop duplicates at the end, in case we want to keep the category separation
        """
        df = self.explode(df, self.ticker_cols)

        main_cols = ["id",
                     "title" if "title" in self.cols_with_ticker else "comment",
                     "permalink", "built_url", "score", "created"]

        all_dfs = []
        for col in self.ticker_cols:
            temp_df = df[[*main_cols, col]]\
                .drop_duplicates(subset=['id', col])
            temp_df["category"] = col
            temp_df = temp_df.rename({col: "ticker"}, axis=1)
            all_dfs.append(temp_df)

        transformed_df = pd.concat(all_dfs, ignore_index=True)

        # can filter counts here if you want
        return self.filter_count(transformed_df, "ticker", min_count)

    def clean_ticker(self, df):
        """clean ticker rows that are empty
        """
        # df['ticker'] = df['ticker'].str.strip()
        df = df.drop_duplicates(subset=['id', 'ticker'])
        # https://stackoverflow.com/questions/29314033/drop-rows-containing-empty-cells-from-a-pandas-dataframe
        df = df[df['ticker'].str.strip().astype(bool)]
        return df.dropna()

    def chart(self):
        df = self.clean_ticker(
            self.transform(
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
            # url='https://www.reddit.com' + alt.datum.permalink
            url=alt.datum.built_url
        ).mark_text(
            align='left',
            dx=-12,
            # dy=0,
            color="white",
            strokeWidth=0,
            strokeOpacity=0,
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
            width=30,
            height=300
        )

        # Data Tables
        created = ranked_text.encode(text='date_str').properties(title='Created Date')
        ticker = ranked_text.encode(text='ticker').properties(title='Stock Ticker')
        score = ranked_text.encode(text='score').properties(title='Upvotes')
        title = ranked_text.encode(
            text="title" if "title" in self.cols_with_ticker else "comment"
        ).properties(
            title='Submission Title' if "title" in self.cols_with_ticker else 'Comment'
        )

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

    def model(self, df):
        df = self.extract_tickers(df)
        df = self.clean_curated(df)
        self.save(df)

        # do it twice just in case
        self.clean_curated()

        # self.plot_tickers(df)  # basic jpg
        self.chart()

        return


class HTMLBase:
    """separate the rendering of index.html from model.
    allows rendering of multiple models to html page.
    otherwise the html would get overwritten with only a specific model.
    """

    def __init__(self, output):
        self.last_updated = dt.now().strftime("%Y-%m-%d %I:%M %p %Z")
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
