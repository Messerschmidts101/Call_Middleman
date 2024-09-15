class RAGChainWithChatHistory:
    def __init__(self, strPromptTemplate, objEmbedding, intRetrieverK, objLLM):
        self.strPromptTemplate = strPromptTemplate
        self.objEmbedding = objEmbedding
        self.intRetrieverK = intRetrieverK
        self.objLLM = objLLM
        self.chat_history = []

        self.objPromptTemplate = PromptTemplate(
            template=self.strPromptTemplate, 
            input_variables=["context", "question"]
        )
        self.objRetriever = self.objEmbedding.as_retriever(search_kwargs={"k": intRetrieverK})
        self.objChain = (
            {"context": self._get_combined_context(), "question": RunnablePassthrough()} | 
            self.objPromptTemplate | 
            self.objLLM
        )

    def _get_combined_context(self):
        # Combine chat history with retrieved documents
        retrieved_docs = self.objRetriever.retrieve()
        combined_context = "\n".join(self.chat_history) + "\n" + "\n".join(retrieved_docs)
        return combined_context

    def add_to_chat_history(self, user_input, response):
        # Update chat history with new interactions
        self.chat_history.append(f"User: {user_input}")
        self.chat_history.append(f"System: {response}")

    def generate_response(self, user_input):
        # Generate a response based on the user's input
        context = self._get_combined_context()
        # Update the RAG chain context
        self.objChain["context"] = context
        response = self.objChain.run(question=user_input)
        # Update chat history
        self.add_to_chat_history(user_input, response)
        return response
