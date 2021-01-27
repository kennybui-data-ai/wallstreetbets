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

    def drilldown_chart(self):
        H = self.highchart
        df = pd.read_csv(self.curated_output, sep=self.delim,
                         converters={
                             "title_ticker": lambda x: self.convert_list(x),
                             "submission_text_ticker": lambda x: self.convert_list(x)
                         }
                         )

        df = self.model(df)

        agg_df = df[["ticker", "id"]].groupby(["ticker"]).nunique().reset_index().dropna()
        agg_df["drilldown"] = agg_df["ticker"]
        data = agg_df.rename({"id": "y", "ticker": "name"}, axis=1).to_dict('records')

        options = {
            'chart': {
                'type': 'column'
            },
            'title': {
                'text': 'Stock Tickers mentioned on Wall Street Bets'
            },
            'subtitle': {
                'text': 'Click the columns to view versions. Source: <a href="https://www.reddit.com/r/wallstreetbets/">wallstreetbets on Reddit</a>.'
            },
            'xAxis': {
                'type': 'stock ticker'
            },
            'yAxis': {
                'title': {
                    'text': 'mentions'
                }

            },
            'legend': {
                'enabled': False
            },
            'plotOptions': {
                'series': {
                    'borderWidth': 0,
                    'dataLabels': {
                        'enabled': True,
                        'format': '{point.y:.1f}'
                    }
                }
            },

            'tooltip': {
                'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}</b> of total<br/>'
            },

        }

        H.set_dict_options(options)
        H.add_data_set(data, 'column', "Tickers", colorByPoint=True)

        drill_df = plot_df.groupby(["ticker", "title/submission"])["ticker"].count()\
            .unstack('title/submission').fillna(0).reset_index().dropna()

        for row in drill_df.itertuples():
            temp_data = [
                ["submission_text", row.submission],
                ["title", row.title]
            ]
            H.add_drilldown_data_set(temp_data, 'column', row.ticker.strip(), name=row.ticker.strip())

        H.save_file("../drilldown")
        return

    def stack_column_chart(self, df):
        H = self.highchart
        df = pd.read_csv(self.curated_output, sep=self.delim,
                         converters={
                             "title_ticker": lambda x: self.convert_list(x),
                             "submission_text_ticker": lambda x: self.convert_list(x)
                         }
                         )

        df = self.model(df)
        df = df.groupby(["ticker", "title/submission"])["ticker"].count()\
            .unstack('title/submission').fillna(0).reset_index().dropna()

        options = {
            'title': {
                'text': 'Stock Ticker mentions on wallstreetbets'
            },

            'xAxis': {
                # 'categories': ['Apples', 'Oranges', 'Pears', 'Grapes', 'Bananas']
                'categories': df["ticker"].tolist()
            },

            'yAxis': {
                'allowDecimals': False,
                'min': 0,
                'title': {
                    'text': 'Number of Mentions'
                }
            },

            'tooltip': {
                'formatter': "function () {\
                                return '<b>' + this.x + '</b><br/>' +\
                                    this.series.name + ': ' + this.y + '<br/>' +\
                                    'Total: ' + this.point.stackTotal;\
                            }"
            },
            'plotOptions': {
                'column': {
                    'stacking': 'normal'
                }
            }
        }

        H.set_dict_options(options)

        H.add_data_set(df["submission"].tolist(), "column", "submission text")
        H.add_data_set(df["title"].tolist(), "column", "title of submission")
        H.save_file("../columnstack")
        return

    def model(self, df):
        df = self.explode(df, self.ticker_cols)

        title_df = df[["id", "title", "built_url", "title_ticker"]].drop_duplicates(subset=['id', 'title_ticker'])
        title_df["title/submission"] = "title"
        title_df = title_df.rename({"title_ticker": "ticker"}, axis=1)

        submission_df = df[["id", "title", "built_url", "submission_text_ticker"]].drop_duplicates(subset=['id', 'submission_text_ticker'])
        submission_df["title/submission"] = "submission"
        submission_df = submission_df.rename({"submission_text_ticker": "ticker"}, axis=1)

        plot_df = pd.concat([title_df, submission_df], ignore_index=True)
        return self.filter_count(plot_df, "ticker", 20)

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
        self.stack_column_chart()
        self.drilldown_chart()
        return
