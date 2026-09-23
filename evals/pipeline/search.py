def search(query, documents):
    terms = set(query.lower().split())
    return sorted(documents, key=lambda doc: len(terms & set(doc.lower().split())), reverse=True)[:5]
