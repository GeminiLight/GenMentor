

class DeepSearchPipeline:
    def __init__(
        self,
        searcher_manager: Optional[SearcherManager] = None,
        source_processor: Optional[SimpleSourceProcessor] = None,
        vectorstore_manager: Optional[VectorStoreManager] = None,
        retriever_k: int = 5,
        pro_mode_multiplier: int = 2,
    ):
        self.searcher_manager = searcher_manager
        self.source_processor = source_processor or SimpleSourceProcessor()
        self.vectorstore_manager = vectorstore_manager or VectorStoreManager()
        self.retriever_k = retriever_k
        self.pro_mode_multiplier = pro_mode_multiplier

    def search(self, query: str, *, max_results: Optional[int] = None, pro_mode: bool = False) -> List[SearchResult]:
        effective_max = max_results or self.searcher_manager.default_max_results
        if pro_mode:
            effective_max = max(effective_max, self.searcher_manager.default_max_results * self.pro_mode_multiplier)
        return self.searcher_manager.search(query, max_results=effective_max)

    def search_and_store(
        self,
        query: str,
        collection_name: str,
        *,
        max_results: Optional[int] = None,
        pro_mode: bool = False,
        persist_directory: Optional[str] = None,
        chunk_size: Optional[int] = None,
    ):
        results = self.search(query, max_results=max_results, pro_mode=pro_mode)
        processed = self.source_processor.process(results, query, chunk_size=chunk_size)
        vectorstore = self.vectorstore_manager.upsert(
            collection_name,
            processed,
            persist_directory=persist_directory,
        )
        return vectorstore, processed

    def retrieve(
        self,
        collection_name: str,
        query: str,
        *,
        k: Optional[int] = None,
        persist_directory: Optional[str] = None,
    ):
        vectorstore = self.vectorstore_manager.load(collection_name, persist_directory=persist_directory)
        retriever = vectorstore.as_retriever(search_kwargs={"k": k or self.retriever_k})
        return retriever.invoke(query)

    def run(
        self,
        query: str,
        collection_name: str,
        *,
        max_results: Optional[int] = None,
        k: Optional[int] = None,
        pro_mode: bool = False,
        persist_directory: Optional[str] = None,
        chunk_size: Optional[int] = None,
    ):
        vectorstore, _ = self.search_and_store(
            query,
            collection_name,
            max_results=max_results,
            pro_mode=pro_mode,
            persist_directory=persist_directory,
            chunk_size=chunk_size,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k or self.retriever_k})
        return retriever.invoke(query)


def build_context(docs: Sequence[Document]) -> str:
    formatted_chunks: List[str] = []
    for idx, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title") if doc.metadata else None
        source = doc.metadata.get("source") if doc.metadata else None
        header_parts = [f"[{idx}]"]
        if title:
            header_parts.append(title)
        if source:
            header_parts.append(f"Source: {source}")
        header = " | ".join(header_parts)
        body = doc.page_content.strip()
        formatted_chunks.append(f"{header}\n{body}")
    return "\n\n".join(formatted_chunks)


def format_docs(docs: Sequence[Document]) -> str:
    return build_context(docs)


def create_deep_search_pipeline(
    *,
    persist_directory: str = "./vectorstore",
    chunk_size: int = 1000,
    chunk_overlap: int = 0,
    split_by: str = "token",
    default_max_results: int = 3,
    retriever_k: int = 5,
    pro_mode_multiplier: int = 2,
) -> DeepSearchPipeline:
    search_client = TavilySearchClient(default_max_results=default_max_results)
    source_processor = SimpleSourceProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        split_by=split_by,
    )
    vectorstore_manager = VectorStoreManager(persist_directory=persist_directory)
    return DeepSearchPipeline(
        search_client=search_client,
        source_processor=source_processor,
        vectorstore_manager=vectorstore_manager,
        retriever_k=retriever_k,
        pro_mode_multiplier=pro_mode_multiplier,
    )


def search_and_store(
    query: str,
    db_collection_name: str,
    db_persist_directory: str = "./vectorstore",
    chunk_size: int = 1000,
    num_results: int = 3,
    *,
    pro_mode: bool = False,
):
    pipeline = create_deep_search_pipeline(
        persist_directory=db_persist_directory,
        chunk_size=chunk_size,
        default_max_results=num_results,
    )
    vectorstore, _ = pipeline.search_and_store(
        query,
        db_collection_name,
        max_results=num_results,
        pro_mode=pro_mode,
        persist_directory=db_persist_directory,
        chunk_size=chunk_size,
    )
    return vectorstore


def search_enhanced_rag(
    query: str,
    db_collection_name: str,
    db_persist_directory: str = "./vectorstore",
    num_results: int = 3,
    num_retrieval_results: int = 5,
    *,
    chunk_size: int = 1000,
    pro_mode: bool = False,
):
    pipeline = create_deep_search_pipeline(
        persist_directory=db_persist_directory,
        chunk_size=chunk_size,
        default_max_results=num_results,
        retriever_k=num_retrieval_results,
    )
    return pipeline.run(
        query,
        db_collection_name,
        max_results=num_results,
        k=num_retrieval_results,
        pro_mode=pro_mode,
        persist_directory=db_persist_directory,
        chunk_size=chunk_size,
    )