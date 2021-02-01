# models are based on WSB flairs or functionality:
# https://www.reddit.com/r/wallstreetbets/wiki/linkflair

# idea is each model might implement unique way of analyzing the data
# also want to support NLP sentiment analysis in the future

from base import ModelBase, HTMLBase, pd, alt


class DueDiligence(ModelBase):
    """DD flair
    get top DD flairs for the day
    subreddit.top does not support DD flair
    need to use search
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

        df = self.extract_tickers(df)
        df = self.clean_curated(df)
        self.save(df)
        # do it twice just in case
        self.clean_curated()

        # self.plot_tickers(df)  # basic jpg
        self.chart_title_submission()
        return


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

    TODO @Mark not sure how you want to implement this.
    or do you want to use specific flairs?
    """

    def __init__(self, **kwargs):
        """init

        kwargs include subreddit, timefilter
        """
        kwargs["search_query"] = ""
        super().__init__(**kwargs)

    def model(self, df):
        """UNUSED. groupby agg count then unstack category title/submission
        was mainly for charting with python-highchart but that lib sucks
        """
        return self.clean(
            df.groupby(["ticker", "title/submission"])["ticker"].count()
            .unstack('title/submission').reset_index()
        )

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
        df = self.clean_curated(df)
        self.save(df)
        # do it twice just in case
        self.clean_curated()

        # self.plot_tickers(df)  # basic jpg
        self.chart_title_submission()
        return


class HTML(HTMLBase):
    def tendies(self):
        self.update_html()
