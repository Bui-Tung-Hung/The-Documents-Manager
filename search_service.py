from typing import List, Dict
from collections import defaultdict
from qdrant_manager import SearchDocument
from models import FileSearchResult
import config_docker as config


class FileSearchService:
    """Service for searching documents grouped by file_id"""
    
    def __init__(self):
        self.searcher = SearchDocument(
            collection_name="TestCollection6",
            embedding_model="bge-m3:latest",
            url=config.url,
            api_key=config.api_key,
        )
        self.searcher.init()
        print("✅ FileSearchService initialized successfully.")
    
    def search_by_file_id(self, query: str, k: int = 50, top_files: int = 5) -> List[FileSearchResult]:
        """
        Search documents and group by file_id, returning top results per file.
        
        Args:
            query: Search query string
            k: Number of documents to retrieve from Qdrant
            top_files: Maximum number of file_ids to return
            
        Returns:
            List of FileSearchResult objects
        """
        # Get search results with scores from Qdrant
        try:
            raw_results = self.searcher.search_with_scores(query, k=k)
        except Exception as e:
            print(f"Error getting results with scores: {e}")
            # Fallback to regular search without scores
            docs = self.searcher.search(query, k=k)
            raw_results = [(doc, 0.5) for doc in docs]  # Default score
        
        if not raw_results:
            return []
        
        # Group results by file_id and find best score for each
        file_groups: Dict[str, Dict] = {}
        
        for doc, score in raw_results:
            file_id = doc.metadata.get('fileID', 'unknown')
            
            # Keep only the best scoring document for each file_id
            if file_id not in file_groups or score > file_groups[file_id]['score']:
                file_groups[file_id] = {
                    'best_doc': doc,
                    'score': float(score),
                    'content': self._truncate_content(doc.page_content)
                }
        
        # Convert to results and sort by score (descending)
        results = []
        for file_id, data in file_groups.items():
            results.append(FileSearchResult(
                file_id=file_id,
                score=round(data['score'], 3),  # Round to 3 decimal places
                content=data['content']
            ))
        
        # Sort by score and limit to top_files
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_files]
    
    def _truncate_content(self, content: str, max_length: int = 200) -> str:
        """
        Truncate content to specified length, preserving word boundaries.
        
        Args:
            content: Original content string
            max_length: Maximum length in characters
            
        Returns:
            Truncated content string
        """
        if len(content) <= max_length:
            return content
        
        # Find last space before max_length to preserve word boundaries
        truncated = content[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return truncated + "..."
