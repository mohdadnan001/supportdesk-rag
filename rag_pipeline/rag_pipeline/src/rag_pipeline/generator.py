from typing import List


class Generator:
    def __init__(self, groq_api_key: str | None = None):
        self.groq_api_key = groq_api_key

    def generate(self, query: str, context_chunks: List[dict]) -> str:
        """Generate an answer given a query and retrieved context chunks."""
        if self.groq_api_key:
            context = "\n\n".join(
                chunk["content"] for chunk in context_chunks
            )
            return self._generate_with_groq(query, context)
        return self._generate_template(query, context_chunks)

    def _generate_template(self, query: str, context_chunks: List[dict]) -> str:
        """Simple template-based answer (no external LLM)."""
        # Use only the top chunk to keep the answer concise
        top_chunk = context_chunks[0] if context_chunks else {}
        content = top_chunk.get("content", "")
        source = top_chunk.get("metadata", {}).get("source", "unknown")

        return (
            f"Based on the support documents, here is the answer:\n\n"
            f"{content}\n\n"
            f"Source: {source}\n\n"
            f"Note: No LLM API key was configured. Set GROQ_API_KEY to use an actual language model for generation."
        )

    def _generate_with_groq(self, query: str, context: str) -> str:
        """Generate answer using Groq API."""
        try:
            from groq import Groq
        except ImportError:
            return self._generate_template(query, context)

        client = Groq(api_key=self.groq_api_key)
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer the user's question using only the provided context. Be concise and direct.",
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}",
                },
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content or "No answer generated."
