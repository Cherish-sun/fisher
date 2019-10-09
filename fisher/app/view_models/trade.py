from app.view_models.book import BookViewModel


class TradeInfo:
    def __init__(self, trade):
        self.total = 0
        self.trades = []
        self._parse(trade)

    def _parse(self, trade):
        self.total = len(trade)
        self.trades = [self._map_to_trade(gift) for gift in trade]

    def _map_to_trade(self, single):
        if single.create_datetime:
            time = single.create_datetime.strftime('%Y-%m-%d')
        else:
            time = '未知'
        return dict(user_name=single.user.nickname
                    , id=single.id,
                    time=time)


class MyTrades:
    def __init__(self, trades_of_mine, trade_of_count):
        self.trades = []
        self.__trades_of_mine = trades_of_mine
        self.__trade_of_count = trade_of_count
        self.trades = self.__parse()

    def __parse(self):
        temp_list = []
        for trade in self.__trades_of_mine:
            t = self.__matching(trade)
            temp_list.append(t)
        return temp_list

    def __matching(self, trade):
        count = 0
        for wish_conut in self.__trade_of_count:
            if trade.isbn == wish_conut['isbn']:
                count = wish_conut['count']
        r = {
            'id': trade.id,
            'book': BookViewModel(trade.get_book),
            'wishes_count': count
        }
        return r
