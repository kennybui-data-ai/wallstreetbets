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
        print("""
   ___             ___  _ ___                      
  / _ \__ _____   / _ \(_) (_)__ ____ ___  _______ 
 / // / // / -_) / // / / / / _ `/ -_) _ \/ __/ -_)
/____/\_,_/\__/ /____/_/_/_/\_, /\__/_//_/\__/\__/ 
                           /___/                   
        """)
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
        print("""
   ___       _ __       ___  _                      _         
  / _ \___ _(_) /_ __  / _ \(_)__ ______ _____ ___ (_)__  ___ 
 / // / _ `/ / / // / / // / (_-</ __/ // (_-<(_-</ / _ \/ _ \\
/____/\_,_/_/_/\_, / /____/_/___/\__/\_,_/___/___/_/\___/_//_/
              /___/                                           
        """)
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
        print("""
   ______           __     _______     __          
  / __/ /____  ____/ /__  /_  __(_)___/ /_____ ____
 _\ \/ __/ _ \/ __/  '_/   / / / / __/  '_/ -_) __/
/___/\__/\___/\__/_/\_\   /_/ /_/\__/_/\_\\__/_/   
                                                   
        """)
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
