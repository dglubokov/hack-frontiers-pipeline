import pandas as pd
import requests as r
from bs4 import BeautifulSoup


class PubmedEPostParams:
    WebEnv = None
    query_key = None
    _count = None

    def __init__(self, pubmed_response):
        parsed_response = BeautifulSoup(pubmed_response, "html.parser")
        self.WebEnv = parsed_response.find("webenv").text
        self.query_key = parsed_response.find("querykey").text
        try:
            self._count = int(parsed_response.find("count").text)
        except AttributeError:
            pass

    @property
    def count(self):
        return self._count or float("inf")

    @count.setter
    def count(self, value):
        self._count = value


class PubmedAdapter:

    def __init__(self, apikey):
        self.apikey = apikey

    def search_pubmed(self, query_params, retmax, date_query=None, use_history=True):
        print(retmax)
        if use_history:
            use_history = "y"
        else:
            use_history = "n"
        query_params_built = [self.field_term_query_builder(**param) for param in query_params]
        param_query = " ".join(query_params_built)
        if date_query:
            param_query = f"english[Language] {param_query} AND {date_query}"
        else:
            param_query = f"english[Language] {param_query}"
        print(param_query)
        response = r.post(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            data={
                "db": "pubmed",
                "term": param_query,
                "retmax": retmax,
                "api_key": self.apikey,
                "usehistory": use_history
            }).text
        print(response)
        return {"raw_query": param_query,
                "raw_response": response,
                "pmids": [item.string for item in BeautifulSoup(response, "html.parser").find_all("id")]}

    # https://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_EPost_
    def create_epost_from_pmids(self, pmids):
        response = r.post("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi",
                          data={"id": ",".join(pmids),
                                "db": "pubmed",
                                "api_key": self.apikey})
        # print(response.text)
        return PubmedEPostParams(response.text)

    def get_articles_from_pmids(self, pmids):
        number_of_pmids = len(pmids)
        epost_params = self.create_epost_from_pmids(pmids)
        epost_params.count = number_of_pmids
        articles = self.batch_fetch_pubmed_abstracts(epost_params, number_of_pmids)
        return articles

    def get_abstracts_from_query(self, query_params, result_limit, date_query=None):
        query_result = self.search_pubmed(query_params, result_limit, date_query=date_query, use_history=True)
        search_params = PubmedEPostParams(query_result["raw_response"])
        abstracts = self.batch_fetch_pubmed_abstracts(search_params, result_limit)
        return abstracts

    # TODO refactor this copypaste and move to POST-requests to pubmed
    # deprecated
    def get_pmid_info(self, pmid):
        response = r.get(
            f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml&api_key={self.apikey}').text
        soup = BeautifulSoup(response, 'html.parser')
        article_attributes = dict()
        if len(soup.find_all('abstracttext')) > 0:
            string = ''
            for x in soup.find_all('abstracttext'):
                try:
                    string = string + '\n' + x.get('label') + ': ' + x.text
                except TypeError:
                    string = string + '\n' + x.text
                article_attributes['abstract'] = string
        else:
            article_attributes['abstract'] = ""

        if soup.find('articletitle') is not None:
            article_attributes["title"] = soup.find('articletitle').text
        else:
            article_attributes["title"] = ""

        if soup.find('year') is not None:
            article_attributes["year"] = soup.find('year').text
        else:
            article_attributes["year"] = ""

        if soup.find('journal') is not None and soup.find('journal').find("title") is not None:
            article_attributes["source"] = soup.find('journal').find("title").text
        else:
            article_attributes["source"] = ""

        return article_attributes

    def batch_fetch_pubmed_abstracts(self, batch_params: PubmedEPostParams, result_limit, batch_size=500):
        results = []
        retstart = 0
        total_number_of_articles = min([batch_params.count, result_limit])
        batch_size = min([batch_size, total_number_of_articles])

        while total_number_of_articles > retstart:
            query = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&WebEnv={batch_params.WebEnv}&query_key={batch_params.query_key}&api_key={self.apikey}&retmax={batch_size}&retstart={retstart}&retmode=xml'
            print(retstart)
            try:
                response = r.get(query)
                pubmed_abstracts = BeautifulSoup(response.content, "html.parser").find_all("pubmedarticle")
                for abstract in pubmed_abstracts:
                    article_abstract = self.parse_pubmed_abstract_element(abstract)
                    results.append(article_abstract)
            except Exception:
                print("Pubmed request failed, going next.")
            finally:
                retstart += batch_size
        return results

    @staticmethod
    def field_term_query_builder(terms, fields, quoted=False, negated=False):
        if quoted:
            query_items = ['"' + term + '"' + field for term in terms for field in fields]
        else:
            query_items = [term + field for term in terms for field in fields]
        query = " OR ".join(query_items)
        if negated:
            return f"NOT ({query})"
        else:
            return f"AND ({query})"

    @staticmethod
    def parse_pubmed_abstract_element(abstract_element):
        article_attributes = {"pmid": abstract_element.find("pmid").text}
        if len(abstract_element.find_all('abstracttext')) > 0:
            string = ''
            for x in abstract_element.find_all('abstracttext'):
                try:
                    string = string + '\n' + x.get('label') + ': ' + x.text
                except TypeError:
                    string = string + '\n' + x.text
                article_attributes['abstract'] = string
        else:
            article_attributes['abstract'] = ""

        if abstract_element.find('articletitle') is not None:
            article_attributes["title"] = abstract_element.find('articletitle').text
        else:
            article_attributes["title"] = ""

        if abstract_element.find('year') is not None:
            article_attributes["year"] = abstract_element.find('year').text
        else:
            article_attributes["year"] = ""

        if abstract_element.find('journal') is not None and abstract_element.find('journal').find("title") is not None:
            article_attributes["source"] = abstract_element.find('journal').find("title").text
        else:
            article_attributes["source"] = ""

        if abstract_element.find('volume') is not None:
            article_attributes["volume"] = abstract_element.find('volume').text
        else:
            article_attributes["volume"] = ""

        if abstract_element.find('issue') is not None:
            article_attributes["issue"] = abstract_element.find('issue').text
        else:
            article_attributes["issue"] = ""
            
        if abstract_element.find('coistatement') is not None:
            article_attributes["COI"] = abstract_element.find('coistatement').text
        else:
            article_attributes["COI"] = ""
            
        if abstract_element.find('language') is not None:
            article_attributes["lang"] = abstract_element.find('language').text
        else:
            article_attributes["lang"] = ""

        if abstract_element.find('medlinepgn') is not None:
            article_attributes["pages"] = abstract_element.find('medlinepgn').text
        else:
            article_attributes["pages"] = ""

        if abstract_element.find_all(reftype="RetractionIn"):
            article_attributes["is_retracted"] = True
            article_attributes["retracted_in"] = [item.findChild("refsource").text for item
                                                  in abstract_element.find_all(reftype="RetractionIn")
                                                  if item.findChild("refsource")]
        else:
            article_attributes["is_retracted"] = False
            article_attributes["retracted_in"] = []

        if abstract_element.find("publicationtype"):
            article_attributes["publication_types"] = [x.text for x in abstract_element.find_all("publicationtype")]                
            
        return article_attributes