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
                 intRetrieverK = 5):
        self.boolCreateDatabase = boolCreateDatabase
        self.strAPIKey = strAPIKey
        self.strPromptTemplate = strPromptTemplate
        self.objEmbedding = self.ingest_database(strIngestPath)
        self.initialize_llm(intLLMSetting,fltTemperature,intRetrieverK)

    def initialize_llm(self, intLLMSetting, fltTemperature, intRetrieverK):
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
            self.objLLM = ChatGroq(temperature=fltTemperature, 
                                   model_name=strModelName, 
                                   groq_api_key=self.strAPIKey)
        elif intLLMSetting == 3:  # HuggingFace LLM
            self.objLLM = HuggingFaceEndpoint(repo_id=strModelName, 
                                              temperature=fltTemperature, 
                                              token=os.environ["HUGGINGFACEHUB_API_TOKEN"])
        elif intLLMSetting == 4: # OpenAI LLM
            self.objLLM = AzureChatOpenAI(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                deployment_name=strModelName,  # Use your specific deployment name
                model=strModelName,  # Or another model you have deployed
                temperature=fltTemperature,
                api_version="2024-02-01"
            )
        if intLLMSetting > 0 and intLLMSetting < 5:
            self.objPromptTemplate = PromptTemplate(template = self.strPromptTemplate, 
                                                    input_variables = ["context", "question"])
            self.objRetriever = self.objEmbedding.as_retriever(search_kwargs={"k": intRetrieverK})
            self.objChain = ({"context": self.objRetriever | self.combine_docs, "question": RunnablePassthrough()} | 
                            self.objPromptTemplate | 
                            self.objLLM)
        else:
            self.objPromptTemplate = PromptTemplate(template = self.strPromptTemplate, 
                                                    input_variables=["question"])
            self.objRetriever = self.objEmbedding.as_retriever(search_kwargs={"k": intRetrieverK})
            self.objChain = ({"question": RunnablePassthrough()} | 
                            self.objPromptTemplate | 
                            self.objLLM)

    def combine_docs(self, docs):
        '''
        This method is a sub process for ingesting database, triggered by ingest_database()
        '''
        return "\n\n".join(doc.page_content for doc in docs)

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