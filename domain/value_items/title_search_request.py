class TitleSearchRequest:
    """Represents a search request for a title."""
    
    def __init__(self, search_text: str = None):
        self.search_text = search_text
