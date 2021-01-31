# models are based on WSB flairs or functionality: https://www.reddit.com/r/wallstreetbets/wiki/linkflair
# idea is each model might potentially implement unique way of analyzing the data
# also want to support NLP sentiment analysis in the future

from base import ModelBase, pd
import altair as alt

# use with caution: https://altair-viz.github.io/user_guide/faq.html#maxrowserror-how-can-i-plot-large-datasets
# alt.data_transformers.disable_max_rows()

# https://github.com/altair-viz/altair/issues/742
# alt.renderers.set_embed_options(theme='dark')  # only for jupyter

# alt.themes.enable("fivethirtyeight")
alt.themes.enable("dark")


class DueDiligence(ModelBase):
    """DD flair

    get top DD flairs for the day
    subreddit.top might be easiest
    """

    def __init__(self, **kwargs):
        """init

        kwargs include subreddit, timefilter
        """
        kwargs["search_query"] = "flair:DD"
        kwargs["sort"] = "top"
        super().__init__(**kwargs)

    def tendies(self):
        """main method
        """
        print("Due Diligence")
        df = self.submissions()
        self.save(df)
        pass


class DailyDiscussion(ModelBase):
    """Daily Discussion flair

    always get new
    TODO sentiment analysis?
    """

    def __init__(self, **kwargs):
        """init

        kwargs include subreddit, timefilter
        """
        kwargs["search_query"] = "flair:\"Daily Discussion\""
        kwargs["sort"] = "new"
        super().__init__(**kwargs)

    def tendies(self):
        """main method
        """
        print("Daily Discussion")
        df = self.submissions(comments=True)
        self.save(df)
        return


class StockTicker(ModelBase):
    """get Stock Tickers from all posts titles and contents

    default searchtype is hot
    default time filter is day

    TODO @Mark not sure how you want to implement this. or do you want to use specific flairs?
    """

    def __init__(self, **kwargs):
        """init

        kwargs include subreddit, timefilter
        """
        kwargs["search_query"] = ""
        super().__init__(**kwargs)

    def chart(self):
        parse_dates = ["created", "last_updated"]
        df = pd.read_csv(self.curated_output, sep=self.delim, parse_dates=parse_dates,
                         converters={
                             "title_ticker": lambda x: self.convert_list(x),
                             "submission_text_ticker": lambda x: self.convert_list(x)
                         }
                         )

        df = self.clean(
            self.transform(df)
        )

        df["date_str"] = df["created"].map(lambda x: x.strftime("%Y-%m-%d %H:%M"))
        df["date"] = df["created"].map(lambda x: x.strftime("%Y-%m-%d"))
        df["date2"] = df["created"].map(lambda x: x.strftime("%Y-%m-%d"))
        data_start = df["date"].min()
        data_end = df["date"].max()

        # brush = alt.selection(type='interval')

        # DATETIME RANGE
        # https://github.com/altair-viz/altair/issues/2008#issuecomment-621428053
        range_start = alt.binding(input="date")
        range_end = alt.binding(input="date")
        select_range_start = alt.selection_single(name="start", fields=["date"], bind=range_start, init={"date": data_start})
        select_range_end = alt.selection_single(name="end", fields=["date"], bind=range_end, init={"date": data_end})
        # slider = alt.binding_range(min=self.timestamp(min(self.datelist)), max=self.timestamp(max(self.datelist)), step=1, name='Created Date')
        # slider_selection = alt.selection_single(name="SelectorName", fields=['created_date'],
        #                                         bind=slider, init={'created': self.timestamp('2021-01-01')})

        selector = alt.selection_single(
            empty='all', fields=['ticker']
        )

        base = alt.Chart(df).transform_filter(
            # slider_selection
            (alt.datum.date2 >= select_range_start.date) & (alt.datum.date2 <= select_range_end.date)
        ).add_selection(
            selector,
            # slider_selection,
            select_range_start, select_range_end
        )

        bars = base.mark_bar().encode(
            # https://stackoverflow.com/questions/52877697/order-bar-chart-in-altair
            x=alt.X('ticker',
                    sort=alt.EncodingSortField(field="ticker", op="count", order='descending'),
                    axis=alt.Axis(title='Stock Tickers')
                    ),
            y=alt.Y("count(id)",
                    axis=alt.Axis(title='Number of Mentions')
                    ),
            color=alt.condition(selector, 'id:O', alt.value('lightgray'), legend=None),
        ).properties(
            width=1700,
            height=650
        )

        # base chart for data tables
        # href: https://altair-viz.github.io/gallery/scatter_href.html
        ranked_text = base.transform_calculate(
            url='https://www.reddit.com' + alt.datum.permalink
        ).mark_text(
            align='left',
            dx=-15,
            dy=0,
            color="white"
        ).encode(
            y=alt.Y('row_number:O', axis=None),
            href='url:N',
            tooltip=['url:N']
            # color=alt.condition(selector,'id:O',alt.value('lightgray'),legend=None),
        ).transform_window(
            # groupby=["ticker"],  # causes overlap
            # https://altair-viz.github.io/user_guide/generated/core/altair.SortField.html#altair.SortField
            sort=[
                alt.SortField("created", "descending"),
                alt.SortField("score", "descending"),
            ],
            row_number='row_number()'
        ).transform_filter(
            selector
        ).transform_window(
            rank='rank(row_number)'
        ).transform_filter(
            # only shows up to 20
            alt.datum.rank < 20
        ).properties(
            width=30,
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

        # Build chart
        chart = alt.vconcat(
            bars,
            text,
            # autosize="fit"
        ).resolve_legend(
            color="independent"
        )

        with open(self.html_output, "w", encoding="utf-8") as f:
            # jinja2 to render
            f.write(self.chart_template.render(
                vega_version=alt.VEGA_VERSION,
                vegalite_version=alt.VEGALITE_VERSION,
                vegaembed_version=alt.VEGAEMBED_VERSION,
                StockTicker=str(chart.to_json(indent=None))
            ))
        return

    def clean(self, df):
        """clean ticker rows that are empty
        """
        df = df.drop_duplicates(subset=['id', 'ticker'])
        return df[df['ticker'].str.strip().astype(bool)]

    def model(self, df):
        """unused. aggregates and counts
        """
        return self.clean(df.groupby(["ticker", "title/submission"])["ticker"].count().unstack('title/submission').reset_index()
                          )

    def transform(self, df):
        df = self.explode(df, self.ticker_cols)

        main_cols = ["id", "title", "permalink", "built_url", "score", "created"]

        title_df = df[[*main_cols, "title_ticker"]].drop_duplicates(subset=['id', 'title_ticker'])
        title_df["title/submission"] = "title"
        title_df = title_df.rename({"title_ticker": "ticker"}, axis=1)

        submission_df = df[[*main_cols, "submission_text_ticker"]].drop_duplicates(subset=['id', 'submission_text_ticker'])
        submission_df["title/submission"] = "submission"
        submission_df = submission_df.rename({"submission_text_ticker": "ticker"}, axis=1)

        plot_df = pd.concat([title_df, submission_df], ignore_index=True)
        return self.filter_count(plot_df, "ticker", 1)

    def tendies(self):
        """main method
        """
        print("Stock Ticker")
        all_dfs = []
        for sort in ["hot", "top", "new", "controversial"]:
            df = self.submissions(sort=sort)
            all_dfs.append(df)

        df = pd.concat(all_dfs, ignore_index=True).drop_duplicates(
            subset=['id'])
        df = self.extract_tickers(df)
        self.save(df)

        # self.plot_tickers(df)  # basic jpg. we're using highchart for python
        self.chart()
        return
