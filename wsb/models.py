# models are based on WSB flairs or functionality:
# https://www.reddit.com/r/wallstreetbets/wiki/linkflair

# idea is each model might implement unique way of analyzing the data
# also want to support NLP sentiment analysis in the future

from base import ModelBase, HTMLBase, pd


class DueDiligence(ModelBase):
    """DD flair
    get top DD flairs for the day
    subreddit.top does not support searching for DD flair
    need to use subreddit.search
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

        self.model(df)

        return


class DailyDiscussion(ModelBase):
    """Daily Discussion flair

    always get new Daily Discussion
    TODO sentiment analysis?
    """

    def __init__(self, **kwargs):
        """init

        kwargs include subreddit, timefilter
        """
        kwargs["search_query"] = 'flair:"Daily Discussion"'
        kwargs["sort"] = "new"
        kwargs["cols_with_ticker"] = ["comment"]
        super().__init__(**kwargs)

    def tendies(self):
        """main method
        """
        print("Daily Discussion")
        df = self.submissions(comments=True)

        self.model(df)

        return


class StockTicker(ModelBase):
    """get Stock Tickers from all posts titles and contents
    default time filter is day as per args in moneyprinter.py

    TODO @Mark not sure how you want to implement this.
    or do you want to use specific flairs?
    """

    def __init__(self, **kwargs):
        """init

        kwargs include subreddit, timefilter
        """
        kwargs["search_query"] = ""
        super().__init__(**kwargs)

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

        self.model(df)

        return


class HTML(HTMLBase):
    def tendies(self):
        self.update_html()
