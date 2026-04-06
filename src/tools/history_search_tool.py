import json
import os

class HistorySearchTool:
    """
    Search into the history knowledge base (JSON file).
    """
    def __init__(self, kb_path: str = "data/history_db.json"):
        self.kb_path = kb_path
        self.data = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.kb_path):
            return []
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def search(self, query: str) -> str:
        """
        Search for historical events, years, figures.
        """
        results = []
        query_lower = query.lower()
        for item in self.data:
            if (query_lower in item['event'].lower() or 
                query_lower in str(item['year']) or
                any(query_lower in f.lower() for f in item['key_figures'])):
                results.append(item)

        if not results:
            return f"Không tìm thấy thông tin phù hợp cho query: '{query}'."
        
        # Format results for the Agent
        output = [f"Event: {r['event']} ({r['year']}) - {r['description']}. Key figures: {', '.join(r['key_figures'])}" for r in results]
        return "\n".join(output)

# Instantiate tool for global use
history_tool = HistorySearchTool()
