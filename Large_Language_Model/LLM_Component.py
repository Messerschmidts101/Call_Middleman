# For embedding of database
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

# For LLM chain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate

#For LLM
from langchain_community.llms import HuggingFaceEndpoint
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI

import os
import uuid
from datetime import datetime
import time

class LLM:
    def __init__(self, intLLMSetting, 
                 strIngestPath, 
                 strPromptTemplate, 
                 strAPIKey = None, 
                 boolCreateDatabase=False, 
                 fltTemperature = 0.1, 
                 intRetrieverK = 5,
                 intLLMAccessory = None):
        self.boolCreateDatabase = boolCreateDatabase
        self.strAPIKey = strAPIKey
        self.strPromptTemplate = strPromptTemplate
        self.objEmbedding = self.ingest_database(strIngestPath)
        self.lisChatHistory = []
        self.intLLMAccessory = intLLMAccessory
        self.initialize_llm(intLLMSetting,
                            fltTemperature,
                            intRetrieverK,
                            intLLMAccessory)

    def initialize_llm(self, intLLMSetting, 
                       fltTemperature, 
                       intRetrieverK,
                       intLLMAccessory):
        '''
        This method creates LLM with their RAG Chain for this class
        '''
        dictLLMSettings = {
            1: "mixtral-8x7b-32768",
            2: "llama3-70b-8192",
            3: "mistralai/Mistral-7B-Instruct-v0.2",
            4: "gpt-4o-mini",
            5: "mixtral-8x7b-32768",
        }
        strModelName = dictLLMSettings.get(intLLMSetting, None)
        if not strModelName:
            raise ValueError(f"Invalid LLM setting: {intLLMSetting}")
            #output list of llm settings
        if intLLMSetting in [1, 2, 5]: # Groq LLM
            if not self.strAPIKey:
                raise ValueError(f"Requires API Key, set value of 'strAPIKey'")
            self.objLLM = ChatGroq(temperature = fltTemperature, 
                                   model_name = strModelName, 
                                   groq_api_key = self.strAPIKey)
        elif intLLMSetting == 3:  # HuggingFace LLM
            self.objLLM = HuggingFaceEndpoint(repo_id = strModelName, 
                                              temperature = fltTemperature, 
                                              token =self.strAPIKey)
        elif intLLMSetting == 4: # OpenAI LLM
            self.objLLM = AzureChatOpenAI(
                api_key = self.strAPIKey,
                deployment_name = strModelName,  # Use your specific deployment name
                model = strModelName,  # Or another model you have deployed
                temperature = fltTemperature,
                api_version = "2024-02-01"
            )

        if intLLMAccessory > 0:
            if intLLMAccessory == 1:
                #just context on RAG
                self.objPromptTemplate = PromptTemplate(template = self.strPromptTemplate, 
                                                        input_variables = ["context", "question"])
                self.objRetriever = self.objEmbedding.as_retriever(search_kwargs={"k": intRetrieverK})
                self.objChain = ({"context": self.objRetriever | self.combine_docs_context, "question": RunnablePassthrough()} | 
                                self.objPromptTemplate | 
                                self.objLLM)
            elif intLLMAccessory == 2:
                raise ValueError(f"To be added soon Chat History only LLM accessory: {intLLMSetting}")
            elif intLLMAccessory == 3:
                # Both context and chat history in RAG
                self.objPromptTemplate = PromptTemplate(
                    template = self.strPromptTemplate, 
                    input_variables=["context", "question", "chat_history"]
                )
                self.objRetriever = self.objEmbedding.as_retriever(search_kwargs={"k": intRetrieverK})
                # Use the updated combine_docs_chat_history function to provide chat history
                self.objChain = ({
                    "context": self.objRetriever | self.combine_docs_context, 
                    "question": RunnablePassthrough(),
                    "chat_history": lambda inputs: self.combine_docs_chat_history()  # Pass the chat history to the chain
                } | self.objPromptTemplate | self.objLLM)
            else:
                raise ValueError(f"Invalid LLM Additions: {intLLMSetting}")
        else:
            self.objPromptTemplate = PromptTemplate(template = self.strPromptTemplate, 
                                                    input_variables=["question"])
            self.objChain = ({"question": RunnablePassthrough()} | 
                            self.objPromptTemplate | 
                            self.objLLM)            

    def combine_docs_context(self, docs):
        '''
        This method is a sub process for ingesting database for context only RAG chains, triggered by ingest_database()
        '''
        return "\n\n".join(doc.page_content for doc in docs)
    
    def combine_docs_chat_history(self):
        '''
        This method combines the chat history entries, ensuring that both User and System responses are properly included.
        '''
        return "\n".join([
            f"User: {dictElement['User']}\nSystem: {dictElement['System']}"
            for dictElement in self.lisChatHistory if 'User' in dictElement and 'System' in dictElement
        ])

    def add_to_chat_history(self, strUserInput, strLLMOutput):
        '''
        This method adds a single dictionary with both User input and System (LLM) output to the chat history.
        '''
        # Update chat history with both User input and System output in the same dictionary
        self.lisChatHistory.append({"User": strUserInput, "System": strLLMOutput})

    def ingest_database(self, strIngestPath):
        '''
        This method converts all files in a directory and outputs a Chroma database on the same location.
        This can happen manually or automatically. 
        You can use this method manually when there is a need to update the knowledge base after this class was insantiated.
        You use this method automatically when insantiating this class and 'boolCreateDatabase is' set to True.
        '''
        objEmbeddingModel = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        strKnowledgeDirectory = f"{strIngestPath}/chroma_embeddings"

        if self.boolCreateDatabase:
            objLoader = DirectoryLoader(strIngestPath, glob="**/*.txt", loader_cls=TextLoader, show_progress=False)
            raw_documents = objLoader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            documents = text_splitter.split_documents(raw_documents)
            return Chroma.from_documents(documents, objEmbeddingModel, persist_directory=strKnowledgeDirectory)
        else:
            return Chroma(embedding_function=objEmbeddingModel, persist_directory=strKnowledgeDirectory)

    def get_response(self, strQuestion, 
                     strOutputPath=None, 
                     boolShowSource = False,
                     intRetries = 3,
                     intDelay = 90,
                     boolVerbose = False):
        if intDelay < 90:
            print('Warning: intDelay is less than 90, setting intDelay to 90 or higher.')
            intDelay = 90
        if boolShowSource:
            objResponseRetriever = self.objRetriever.get_relevant_documents(strQuestion)
        else:
            objResponseRetriever = None
        strResponse = self.retry_chain_invoke(strQuestion,intRetries,intDelay,boolVerbose)
        if self.intLLMAccessory in [2,3]:
            self.add_to_chat_history(strQuestion,strResponse)
            if boolVerbose:
                print('\n-----','Verbose || Chat History: ', self.lisChatHistory, '\n-----')
        if strOutputPath:
            self.save_response(strResponse, strOutputPath)
        return strResponse,objResponseRetriever

    def retry_chain_invoke(self, strQuestion, intRetries, intDelay, boolVerbose):
        for intAttempt in range(intRetries):
            try:
                strResponse = self.objChain.invoke(strQuestion)
                return strResponse.content
            except AttributeError:
                return self.objChain.invoke(strQuestion)
            except Exception as e:
                if intAttempt < intRetries - 1:
                    if boolVerbose:
                        print(f'Error {intAttempt}: {e}. Retrying in {intDelay} seconds')
                    time.sleep(intDelay)
                else:
                    raise RuntimeError(f"Failed after {intRetries} attempts: {e}")

    def save_response(self, strResponse, strOutputPath):
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4()
        output_file_path = os.path.join(strOutputPath, f'LLM_response_{current_datetime}_{unique_id}.txt')
        
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(strResponse)