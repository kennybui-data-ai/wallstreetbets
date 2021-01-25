# models are based on WSB flairs or functionality: https://www.reddit.com/r/wallstreetbets/wiki/linkflair
# idea is each model might potentially implement unique way of analyzing the data
# also want to support NLP sentiment analysis in the future

from base import ModelBase, pd


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
        df, output_path = self.submissions()
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
        df, output_path = self.submissions(comments=True)
        pass


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

    def tendies(self):
        """main method
        """
        print("Stock Ticker")
        all_dfs = []
        for sort in ["hot", "top", "new", "controversial"]:
            df, output_path = self.submissions(sort=sort)
            all_dfs.append(df)

        final_df = pd.concat(all_dfs)
        final_df.to_csv(
            output_path,
            # sep="|"
        )
        pass
