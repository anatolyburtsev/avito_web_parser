from urllib.parse import urlencode


class AvitoUrl:
    _base_url = "https://www.avito.ru/moskva"
    _max_price = "pmax"
    _max_price_value = None
    _min_price = "pmin"
    _min_price_value = None
    _search_query = "q"
    _search_query_value = None
    # _category = "tovary_dlya_kompyutera"
    # https://www.avito.ru/moskva/tovary_dlya_kompyutera/klaviatury_i_myshi?pmax=4500&pmin=2500&q=apple+trackpad+2

    def __init__(self, query):
        query = query.strip()#.replace(" ", "+")
        self._search_query_value = query

    def set_prices(self, min_price, max_price):
        self._min_price_value = min_price
        self._max_price_value = max_price
        return self

    def get_url(self):
        params = {}
        if self._max_price_value:
            params[self._max_price] = self._max_price_value
        if self._min_price_value:
            params[self._min_price] = self._min_price_value

        params[self._search_query] = self._search_query_value

        return self._base_url + "?" + urlencode(params, encoding="utf-8")


if __name__ == "__main__":
    a = AvitoUrl("apple trackpad 2").set_prices(2500, 4500)

    print(a.get_url())
