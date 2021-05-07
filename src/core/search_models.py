from typing import List
from django.contrib.postgres.search import SearchQuery


class FullTextSearchModel:

    def __init__(self, phrase: str = None, keywords: List[str] = None, country_name_or_code: str = None):
        self.phrase: str = phrase
        self.keywords: List[str] = keywords
        self.country_name_or_code: str = country_name_or_code

    def validate(self):
        if not self.phrase and not self.country_name_or_code and not self.keywords:
            return False
        return True

    def generate_search_query(self):
        queries = list()
        if self.keywords is not None:
            for item in self.keywords:
                queries.append(SearchQuery(item.strip(), search_type='plain'))

        if self.phrase is not None:
            queries.append(SearchQuery(self.phrase.strip(), search_type='phrase'))

        if self.country_name_or_code is not None:
            if len(self.country_name_or_code) <= 3:
                from django_countries.fields import Country
                country_name = Country(code=self.country_name_or_code).name
                queries.append(SearchQuery(country_name, search_type='phrase'))
                queries.append(SearchQuery(self.country_name_or_code, search_type='plain'))
            else:
                queries.append(SearchQuery(self.country_name_or_code, search_type='phrase'))
                from django_countries import countries
                reversed_countries = {str(value).lower(): key for (key, value) in countries}
                if self.country_name_or_code.lower() in reversed_countries:
                    queries.append(SearchQuery(reversed_countries[self.country_name_or_code.lower()], search_type='plain'))

        final_query: SearchQuery = queries[0]
        for idx in range(1, len(queries)):
            final_query = final_query | queries[idx]

        return final_query
