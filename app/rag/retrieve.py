from app.rag import store


def get_relevant_docs(query):
    if store.vectorstore is None:
        return []

    docs = store.vectorstore.similarity_search_with_score(query, k=3)

    relevant_docs = []

    for doc, score in docs:
        print("Score:", score)

        if score < 0.7:  # 🔥 important
            relevant_docs.append(doc)

    return relevant_docs