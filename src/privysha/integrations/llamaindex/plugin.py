# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
LlamaIndex Integration for PrivySHA

This module provides seamless integration with LlamaIndex components,
allowing PrivySHA to secure and optimize queries and prompts within
LlamaIndex pipelines.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from llama_index.core import QueryEngine, VectorStoreIndex
    from llama_index.core.base.base_query_engine import BaseQueryEngine
    from llama_index.core.base.base_retriever import BaseRetriever
    from llama_index.core.llms import LLM, CustomLLM
    from llama_index.core.prompts import PromptTemplate
    from llama_index.core.schema import QueryBundle, Document

    LLAMAINDEX_AVAILABLE = True
else:
    try:
        from llama_index.core import QueryEngine, VectorStoreIndex
        from llama_index.core.base.base_query_engine import BaseQueryEngine
        from llama_index.core.base.base_retriever import BaseRetriever
        from llama_index.core.llms import LLM, CustomLLM
        from llama_index.core.prompts import PromptTemplate
        from llama_index.core.schema import QueryBundle, Document

        LLAMAINDEX_AVAILABLE = True
    except ImportError:
        LLAMAINDEX_AVAILABLE = False

        class QueryEngine:
            pass

        class VectorStoreIndex:
            @classmethod
            def from_documents(cls, *args: Any, **kwargs: Any) -> "VectorStoreIndex":
                return cls()

        class BaseQueryEngine:
            def query(self, query_bundle: Any) -> Any:
                return None

            async def aquery(self, query_bundle: Any) -> Any:
                return None

        class BaseRetriever:
            def retrieve(self, query_bundle: Any) -> List[Any]:
                return []

            async def aretrieve(self, query_bundle: Any) -> List[Any]:
                return []

        class LLM:
            model_name: str = "llm"

            def complete(self, prompt: str, **kwargs: Any) -> str:
                return prompt

        class CustomLLM:
            pass

        class PromptTemplate:
            def __init__(self, template: str, **kwargs: Any) -> None:
                self.template = template

            def format(self, **kwargs: Any) -> str:
                return self.template

        class QueryBundle:
            def __init__(
                self,
                query_str: str,
                custom_embedding_strs: Any = None,
                embedding_strs: Any = None,
            ) -> None:
                self.query_str = query_str
                self.custom_embedding_strs = custom_embedding_strs
                self.embedding_strs = embedding_strs

        class Document:
            def __init__(
                self,
                text: str,
                metadata: Optional[Dict[str, Any]] = None,
                id_: Optional[str] = None,
            ) -> None:
                self.text = text
                self.metadata = metadata or {}
                self.id_ = id_


from ...utils.dropin import process, _coerce_process_output


def _optimize_prompt_text(
    text: str,
    *,
    privacy: bool,
    token_budget: int,
    debug_metrics: bool,
) -> tuple[str, Optional[Dict[str, Any]]]:
    """Run process() and return optimized text plus optional metrics."""
    if debug_metrics:
        result = cast(
            Dict[str, Any],
            process(
                text,
                privacy=privacy,
                token_budget=token_budget,
                return_metrics=True,
            ),
        )
        return str(result["optimized"]), result
    return (
        _coerce_process_output(
            process(text, privacy=privacy, token_budget=token_budget),
            text,
        ),
        None,
    )


class PrivySHAPromptTemplate(PromptTemplate):
    """
    LlamaIndex PromptTemplate wrapper that applies PrivySHA optimization.

    This wrapper automatically processes prompts through PrivySHA's
    security and optimization pipeline before using them in LlamaIndex.
    """

    def __init__(
        self,
        template: str,
        privacy: bool = True,
        token_budget: int = 1200,
        debug_metrics: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize PrivySHA-enhanced prompt template.

        Args:
            template: Prompt template string
            privacy: Enable privacy features
            token_budget: Token budget for optimization
            debug_metrics: Return optimization metrics
        """
        if not LLAMAINDEX_AVAILABLE:
            raise ImportError(
                "LlamaIndex is not installed. Install with: pip install llama-index\n"
                "Or use the standalone PrivySHA functions instead."
            )

        super().__init__(template=template, **kwargs)
        self.privacy = privacy
        self.token_budget = token_budget
        self.debug_metrics = debug_metrics
        self._last_metrics: Optional[Dict[str, Any]] = None

    def format(self, **kwargs: Any) -> str:
        """
        Format the template with input variables and apply PrivySHA optimization.

        Args:
            **kwargs: Input variable values

        Returns:
            Optimized prompt string
        """
        # Format the template normally
        formatted_prompt = super().format(**kwargs)

        # Apply PrivySHA optimization
        if self.debug_metrics:
            result = cast(
                Dict[str, Any],
                process(
                    formatted_prompt,
                    privacy=self.privacy,
                    token_budget=self.token_budget,
                    return_metrics=True,
                ),
            )
            self._last_metrics = result
            return str(result["optimized"])
        return _coerce_process_output(
            process(
                formatted_prompt,
                privacy=self.privacy,
                token_budget=self.token_budget,
            ),
            formatted_prompt,
        )

    def get_last_metrics(self) -> Optional[Dict[str, Any]]:
        """Get metrics from the last prompt processing."""
        return self._last_metrics


class PrivySHALLM(CustomLLM):
    """
    LlamaIndex LLM wrapper that applies PrivySHA security and optimization.

    This wrapper intercepts all prompts sent to the LLM and processes them
    through PrivySHA's pipeline before forwarding to the actual LLM.
    """

    context_window: int = 4096
    num_output: int = 256
    model_name: str = "privysha_llm"

    def __init__(
        self,
        llm: LLM,
        privacy: bool = True,
        token_budget: int = 1200,
        debug_metrics: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize PrivySHA-enhanced LLM wrapper.

        Args:
            llm: Base LLM to wrap
            privacy: Enable privacy features
            token_budget: Token budget for optimization
            debug_metrics: Return optimization metrics
        """
        super().__init__(**kwargs)
        self.llm = llm
        self.privacy = privacy
        self.token_budget = token_budget
        self.debug_metrics = debug_metrics
        self._last_metrics: Optional[Dict[str, Any]] = None
        self.model_name = f"privysha_{llm.model_name}"

    def _get_prompt_type(self, prompt: str) -> str:
        """Determine prompt type for specialized processing."""
        prompt_lower = prompt.lower()
        if "query" in prompt_lower or "search" in prompt_lower:
            return "query"
        elif "summarize" in prompt_lower or "summary" in prompt_lower:
            return "summary"
        elif "analyze" in prompt_lower or "analysis" in prompt_lower:
            return "analysis"
        else:
            return "general"

    def complete(self, prompt: str, **kwargs: Any) -> str:
        """
        Process prompt through PrivySHA and forward to LLM.

        Args:
            prompt: Input prompt
            **kwargs: Additional completion arguments

        Returns:
            LLM response
        """
        # Apply PrivySHA optimization
        if self.debug_metrics:
            result = cast(
                Dict[str, Any],
                process(
                    prompt,
                    privacy=self.privacy,
                    token_budget=self.token_budget,
                    return_metrics=True,
                ),
            )
            self._last_metrics = result
            optimized_prompt = str(result["optimized"])
        else:
            optimized_prompt = _coerce_process_output(
                process(
                    prompt, privacy=self.privacy, token_budget=self.token_budget
                ),
                prompt,
            )

        # Forward to actual LLM
        return str(self.llm.complete(optimized_prompt, **kwargs))

    def complete_request(self, prompt: str, **kwargs: Any) -> str:
        """Process complete request with PrivySHA optimization."""
        return self.complete(prompt, **kwargs)

    def get_last_metrics(self) -> Optional[Dict[str, Any]]:
        """Get metrics from the last prompt processing."""
        return self._last_metrics


class PrivySHAQueryEngine(BaseQueryEngine):
    """
    LlamaIndex QueryEngine wrapper that applies PrivySHA optimization.

    This wrapper processes queries through PrivySHA's security and
    optimization pipeline before sending them to the underlying query engine.
    """

    def __init__(
        self,
        query_engine: BaseQueryEngine,
        privacy: bool = True,
        token_budget: int = 1200,
        debug_metrics: bool = False,
        optimize_queries: bool = True,
        optimize_retrieval: bool = True,
    ) -> None:
        """
        Initialize PrivySHA-enhanced query engine.

        Args:
            query_engine: Base query engine to wrap
            privacy: Enable privacy features
            token_budget: Token budget for optimization
            debug_metrics: Return optimization metrics
            optimize_queries: Optimize query prompts
            optimize_retrieval: Optimize retrieval queries
        """
        self._query_engine = query_engine
        self.privacy = privacy
        self.token_budget = token_budget
        self.debug_metrics = debug_metrics
        self.optimize_queries = optimize_queries
        self.optimize_retrieval = optimize_retrieval
        self._last_metrics: Optional[Dict[str, Any]] = None

    def query(self, query_bundle: QueryBundle) -> Any:
        """
        Process query through PrivySHA and forward to query engine.

        Args:
            query_bundle: Query bundle containing the query

        Returns:
            Query response
        """
        query_str = query_bundle.query_str

        # Apply PrivySHA optimization to query
        if self.optimize_queries:
            optimized_query, metrics = _optimize_prompt_text(
                query_str,
                privacy=self.privacy,
                token_budget=self.token_budget,
                debug_metrics=self.debug_metrics,
            )
            if metrics is not None:
                self._last_metrics = metrics

            # Create new query bundle with optimized query
            optimized_bundle = QueryBundle(
                query_str=optimized_query,
                custom_embedding_strs=query_bundle.custom_embedding_strs,
                embedding_strs=query_bundle.embedding_strs,
            )
        else:
            optimized_bundle = query_bundle

        # Forward to actual query engine
        return self._query_engine.query(optimized_bundle)

    def get_last_metrics(self) -> Optional[Dict[str, Any]]:
        """Get metrics from the last query processing."""
        return self._last_metrics

    async def aquery(self, query_bundle: QueryBundle) -> Any:
        """Async query with PrivySHA optimization."""
        query_str = query_bundle.query_str

        # Apply PrivySHA optimization to query
        if self.optimize_queries:
            optimized_query, metrics = _optimize_prompt_text(
                query_str,
                privacy=self.privacy,
                token_budget=self.token_budget,
                debug_metrics=self.debug_metrics,
            )
            if metrics is not None:
                self._last_metrics = metrics

            # Create new query bundle with optimized query
            optimized_bundle = QueryBundle(
                query_str=optimized_query,
                custom_embedding_strs=query_bundle.custom_embedding_strs,
                embedding_strs=query_bundle.embedding_strs,
            )
        else:
            optimized_bundle = query_bundle

        # Forward to actual query engine
        return await self._query_engine.aquery(optimized_bundle)


class PrivySHARetriever(BaseRetriever):
    """
    LlamaIndex Retriever wrapper that applies PrivySHA optimization.

    This wrapper processes retrieval queries through PrivySHA's
    optimization pipeline before sending them to the underlying retriever.
    """

    def __init__(
        self,
        retriever: BaseRetriever,
        privacy: bool = True,
        token_budget: int = 1200,
        debug_metrics: bool = False,
    ) -> None:
        """
        Initialize PrivySHA-enhanced retriever.

        Args:
            retriever: Base retriever to wrap
            privacy: Enable privacy features
            token_budget: Token budget for optimization
            debug_metrics: Return optimization metrics
        """
        self._retriever = retriever
        self.privacy = privacy
        self.token_budget = token_budget
        self.debug_metrics = debug_metrics
        self._last_metrics: Optional[Dict[str, Any]] = None

    def retrieve(self, query_bundle: QueryBundle) -> List[Document]:
        """
        Process query through PrivySHA and forward to retriever.

        Args:
            query_bundle: Query bundle containing the query

        Returns:
            Retrieved documents
        """
        query_str = query_bundle.query_str

        optimized_query, metrics = _optimize_prompt_text(
            query_str,
            privacy=self.privacy,
            token_budget=self.token_budget,
            debug_metrics=self.debug_metrics,
        )
        if metrics is not None:
            self._last_metrics = metrics

        # Create new query bundle with optimized query
        optimized_bundle = QueryBundle(
            query_str=optimized_query,
            custom_embedding_strs=query_bundle.custom_embedding_strs,
            embedding_strs=query_bundle.embedding_strs,
        )

        # Forward to actual retriever
        return cast(List[Document], self._retriever.retrieve(optimized_bundle))

    def get_last_metrics(self) -> Optional[Dict[str, Any]]:
        """Get metrics from the last retrieval processing."""
        return self._last_metrics

    async def aretrieve(self, query_bundle: QueryBundle) -> List[Document]:
        """Async retrieval with PrivySHA optimization."""
        query_str = query_bundle.query_str

        optimized_query, metrics = _optimize_prompt_text(
            query_str,
            privacy=self.privacy,
            token_budget=self.token_budget,
            debug_metrics=self.debug_metrics,
        )
        if metrics is not None:
            self._last_metrics = metrics

        # Create new query bundle with optimized query
        optimized_bundle = QueryBundle(
            query_str=optimized_query,
            custom_embedding_strs=query_bundle.custom_embedding_strs,
            embedding_strs=query_bundle.embedding_strs,
        )

        # Forward to actual retriever
        return cast(List[Document], await self._retriever.aretrieve(optimized_bundle))


# Convenience functions for easy integration
def wrap_prompt_template(
    template: str,
    privacy: bool = True,
    token_budget: int = 1200,
    debug_metrics: bool = False,
) -> PrivySHAPromptTemplate:
    """
    Create a PrivySHA-enhanced prompt template.

    Args:
        template: Prompt template string
        privacy: Enable privacy features
        token_budget: Token budget for optimization
        debug_metrics: Return optimization metrics

    Returns:
        PrivySHA-enhanced prompt template
    """
    return PrivySHAPromptTemplate(
        template=template,
        privacy=privacy,
        token_budget=token_budget,
        debug_metrics=debug_metrics,
    )


def wrap_llm(
    llm: LLM,
    privacy: bool = True,
    token_budget: int = 1200,
    debug_metrics: bool = False,
) -> PrivySHALLM:
    """
    Wrap an LLM with PrivySHA optimization.

    Args:
        llm: LLM to wrap
        privacy: Enable privacy features
        token_budget: Token budget for optimization
        debug_metrics: Return optimization metrics

    Returns:
        PrivySHA-enhanced LLM
    """
    return PrivySHALLM(
        llm=llm, privacy=privacy, token_budget=token_budget, debug_metrics=debug_metrics
    )


def wrap_query_engine(
    query_engine: BaseQueryEngine,
    privacy: bool = True,
    token_budget: int = 1200,
    debug_metrics: bool = False,
    optimize_queries: bool = True,
    optimize_retrieval: bool = True,
) -> PrivySHAQueryEngine:
    """
    Wrap a query engine with PrivySHA optimization.

    Args:
        query_engine: Query engine to wrap
        privacy: Enable privacy features
        token_budget: Token budget for optimization
        debug_metrics: Return optimization metrics
        optimize_queries: Optimize query prompts
        optimize_retrieval: Optimize retrieval queries

    Returns:
        PrivySHA-enhanced query engine
    """
    return PrivySHAQueryEngine(
        query_engine=query_engine,
        privacy=privacy,
        token_budget=token_budget,
        debug_metrics=debug_metrics,
        optimize_queries=optimize_queries,
        optimize_retrieval=optimize_retrieval,
    )


def wrap_retriever(
    retriever: BaseRetriever,
    privacy: bool = True,
    token_budget: int = 1200,
    debug_metrics: bool = False,
) -> PrivySHARetriever:
    """
    Wrap a retriever with PrivySHA optimization.

    Args:
        retriever: Retriever to wrap
        privacy: Enable privacy features
        token_budget: Token budget for optimization
        debug_metrics: Return optimization metrics

    Returns:
        PrivySHA-enhanced retriever
    """
    return PrivySHARetriever(
        retriever=retriever,
        privacy=privacy,
        token_budget=token_budget,
        debug_metrics=debug_metrics,
    )


class PrivySHAPostProcessor:
    """
    LlamaIndex post-processor that applies PrivySHA security and optimization
    to query results and responses.

    This post-processor ensures that all text returned from LlamaIndex
    pipelines is properly secured and optimized.
    """

    def __init__(
        self,
        privacy: bool = True,
        token_budget: int = 1200,
        debug_metrics: bool = False,
    ) -> None:
        """
        Initialize PrivySHA post-processor.

        Args:
            privacy: Enable privacy features
            token_budget: Token budget for optimization
            debug_metrics: Return optimization metrics
        """
        if not LLAMAINDEX_AVAILABLE:
            raise ImportError(
                "LlamaIndex is not installed. Install with: pip install llama-index\n"
                "Or use the standalone PrivySHA functions instead."
            )

        self.privacy = privacy
        self.token_budget = token_budget
        self.debug_metrics = debug_metrics
        self._last_metrics: Optional[Dict[str, Any]] = None

    def postprocess_nodes(
        self, nodes: List[Any], **kwargs: Any
    ) -> List[Any]:
        """
        Apply PrivySHA processing to document nodes.

        Args:
            nodes: List of document nodes to process
            **kwargs: Additional arguments

        Returns:
            List of processed document nodes
        """
        processed_nodes: List[Any] = []

        for node in nodes:
            if hasattr(node, "text") and node.text:
                # Process the node text through PrivySHA
                result = process(
                    node.text,
                    privacy=self.privacy,
                    token_budget=self.token_budget,
                    return_metrics=self.debug_metrics,
                )

                # Create new document with processed text
                if isinstance(result, str):
                    processed_text = result
                else:
                    processed_text = result.get("optimized", node.text)
                    if self.debug_metrics:
                        self._last_metrics = result.get("metrics", {})

                # Create new node with processed text
                if hasattr(node, "copy"):
                    processed_node = node.copy()
                    processed_node.text = processed_text
                else:
                    # Fallback for different node types
                    processed_node = Document(
                        text=processed_text,
                        metadata=getattr(node, "metadata", {}),
                        id_=getattr(node, "id_", None),
                    )

                processed_nodes.append(processed_node)
            else:
                processed_nodes.append(node)

        return processed_nodes

    def postprocess_query(self, query_str: str, **kwargs: Any) -> str:
        """
        Apply PrivySHA processing to query string.

        Args:
            query_str: Query string to process
            **kwargs: Additional arguments

        Returns:
            Processed query string
        """
        result = process(
            query_str,
            privacy=self.privacy,
            token_budget=self.token_budget,
            return_metrics=self.debug_metrics,
        )

        if isinstance(result, str):
            return result
        if self.debug_metrics:
            self._last_metrics = cast(Dict[str, Any], result.get("metrics", {}))
        return str(result.get("optimized", query_str))

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the last processing metrics.

        Returns:
            Dictionary of processing metrics
        """
        return self._last_metrics or {}


def create_privysha_index(
    documents: List[Document],
    llm: LLM,
    privacy: bool = True,
    token_budget: int = 1200,
    debug_metrics: bool = False,
    **index_kwargs: Any,
) -> VectorStoreIndex:
    """
    Create a PrivySHA-enhanced VectorStoreIndex.

    Args:
        documents: Documents to index
        llm: LLM to use with PrivySHA optimization
        privacy: Enable privacy features
        token_budget: Token budget for optimization
        debug_metrics: Return optimization metrics
        **index_kwargs: Additional index arguments

    Returns:
        PrivySHA-enhanced VectorStoreIndex
    """
    # Wrap the LLM with PrivySHA
    privysha_llm = wrap_llm(llm, privacy, token_budget, debug_metrics)

    # Create index with PrivySHA-enhanced LLM
    index = VectorStoreIndex.from_documents(
        documents, llm=privysha_llm, **index_kwargs)

    return cast(VectorStoreIndex, index)
