from __future__ import annotations

from typing import List, Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel

from langchain.schema import BaseRetriever, Document
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.requests import TextRequestsWrapper


class WebSearchRetriever(BaseRetriever, BaseModel):
    search_wrapper: GoogleSearchAPIWrapper
    requests_wrapper: TextRequestsWrapper
    num_results: int = 10
    
    @classmethod
    def make(cls, num_results, google_api_key=None, google_cse_id=None, **kwargs) -> WebSearchRetriever:
        search_wrapper = GoogleSearchAPIWrapper(
            google_api_key=google_api_key,
            google_cse_id=google_cse_id)
        requests_wrapper = TextRequestsWrapper()
        
        return cls(
            search_wrapper=search_wrapper,
            requests_wrapper=requests_wrapper,
            num_results=num_results,
            **kwargs)

    def get_relevant_documents(self, query: str) -> List[Document]:
        search_results = self.search_wrapper.results(query, num_results=self.num_results)

        results = []
        for r in search_results:
            url = r["link"]
            page = self.requests_wrapper.get(url)
            soup = BeautifulSoup(page, "html.parser")
            results.append(Document(page_content=soup.get_text(), metadata={"source":r["link"]}))
        
        return results

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        #TODO: Implement this
        return self.get_relevant_documents(query)
