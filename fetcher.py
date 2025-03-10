import requests
import pandas as pd
import re
from typing import List, Dict, Optional

class PubMedFetcher:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self, email: str):
        self.email = email

    def fetch_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """Fetch papers based on the query from PubMed API."""
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "email": self.email,
        }
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []

        return self._fetch_paper_details(ids)

    def _fetch_paper_details(self, ids: List[str]) -> List[Dict]:
        """Fetch detailed paper information given a list of IDs."""
        id_str = ",".join(ids)
        params = {
            "db": "pubmed",
            "id": id_str,
            "retmode": "xml",
            "email": self.email,
        }
        response = requests.get(self.FETCH_URL, params=params)
        response.raise_for_status()
        return self._parse_xml(response.text)

    def _parse_xml(self, xml_data: str) -> List[Dict]:
        """Extract paper details from XML response."""
        # Implement XML parsing (use xml.etree.ElementTree or BeautifulSoup)
        # Extract Title, Authors, Affiliations, Corresponding Author, etc.
        return []  # Placeholder

    def filter_non_academic_authors(self, papers: List[Dict]) -> List[Dict]:
        """Identify and filter papers with non-academic authors."""
        company_keywords = ["Pharma", "Biotech", "Laboratories", "Inc.", "Ltd."]
        
        def is_non_academic(affiliation: str) -> bool:
            return any(keyword in affiliation for keyword in company_keywords)
        
        for paper in papers:
            non_academic_authors = [
                author["name"] for author in paper["authors"]
                if is_non_academic(author["affiliation"])
            ]
            paper["non_academic_authors"] = non_academic_authors
        return [paper for paper in papers if paper["non_academic_authors"]]

    def save_to_csv(self, papers: List[Dict], filename: str):
        """Save results to a CSV file."""
        df = pd.DataFrame(papers)
        df.to_csv(filename, index=False)

