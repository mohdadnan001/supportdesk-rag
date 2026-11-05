from rag_pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()

    # Step 1: Ingest documents
    print("Ingesting documents...")
    pipeline.ingest("data/raw")

    # Step 2: Query
    question = input("\nEnter your question: ")
    result = pipeline.query(question)

    print("\n--- Answer ---")
    print(result["answer"])
    print("\n--- Sources ---")
    for src in result["sources"]:
        print(f"- {src}")


if __name__ == "__main__":
    main()
