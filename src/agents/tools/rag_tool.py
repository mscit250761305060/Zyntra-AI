import logging

logger = logging.getLogger("zyntra.rag_tool")

def rag_search_tool(query: str, user_id: str) -> str:
    """Searches the user's uploaded documents (PDF, DOCX, TXT, CSV) to answer questions based on their personal data or knowledge base. Provide the search query. ONLY use this when the user asks about their documents."""
    from src.services.rag_service import rag_service
    
    try:
        results = rag_service.search(user_id=user_id, query=query, n_results=3)
        if not results:
            return "No relevant information found in the user's uploaded documents."
            
        formatted_results = "Found the following information in the user's documents:\n\n"
        for i, res in enumerate(results):
            filename = res['metadata'].get('filename', 'Unknown document')
            formatted_results += f"Source {i+1} ({filename}):\n"
            formatted_results += f"{res['text']}\n\n"
            
        return formatted_results
    except Exception as e:
        logger.error(f"Error in RAG tool: {e}")
        return f"Error searching documents: {str(e)}"
