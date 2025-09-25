def __init__(self, api_key: Optional[str] = None, country: str = None):
    self.api_key = api_key or os.getenv("NEWSAPI_KEY") or os.getenv("NEWS_API_KEY")
    self.country = (country or os.getenv("NEWSAPI_COUNTRY") or "us").lower()

