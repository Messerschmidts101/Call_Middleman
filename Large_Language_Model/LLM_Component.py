# For embedding of database
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

# For LLM chain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate

#For LLM\
from langchain_groq import ChatGroq

import os
import uuid
from datetime import datetime
import time
#from LLM_Model.LLM_Context_And_Rules import Personas

class LLM:
    '''
    Requires the following:
        1. intLLMSetting
        2. strAPIKey 
        3. strInjestPath
        4. strPromptTemplate (Optional)
        5. boolCreateDatabase (Optional)
    '''
    error_list = ['langchain_core.messages.ai.AIMessage', 'RateLimitError']
    def __init__(self,intLLMSetting:int,
                 strAPIKey:str,
                 strInjestPath:str,
                 strPromptTemplate:str,
                 boolCreateDatabase:bool = False):
        self.boolCreateDatabase = boolCreateDatabase
        self.objEmbedding = self.ingest_database(strInjestPath)
        self.strAPIKey = strAPIKey
        self.strPromptTemplate = strPromptTemplate
        if intLLMSetting == 1:
            #Step 1: Load LLM
            self.objLLM = ChatGroq(temperature=.1, model_name="mixtral-8x7b-32768", groq_api_key=self.strAPIKey)
            #Step 2: Load Template
            self.objPromptTemplate = PromptTemplate(
                template = self.strPromptTemplate,
                input_variables=["context", "question"]
            )
            #Step 3: Load Chain
            self.objRetriever = self.objEmbedding.as_retriever(search_kwargs={"k": 4}) 
            self.objChain = ( {"context": self.objRetriever | self.combine_docs ,"question": RunnablePassthrough()} |
                                self.objPromptTemplate |
                                self.objLLM 
                             )
        if intLLMSetting == 2:
            #Step 1: Load LLM
            self.objLLM = ChatGroq(temperature=.1, model_name="llama3-70b-8192", groq_api_key=self.strAPIKey)
            #Step 2: Load Template
            self.objPromptTemplate = PromptTemplate(
                template = self.strPromptTemplate,
                input_variables=["context", "question"]
            )
            #Step 3: Load Chain
            self.objRetriever = self.objEmbedding.as_retriever(search_kwargs={"k": 5}) 
            self.objChain = ( {"context": self.objRetriever | self.combine_docs ,"question": RunnablePassthrough()} |
                                self.objPromptTemplate |
                                self.objLLM 
                             )
            
    def combine_docs(self,docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def ingest_database(self,strInjestPath):
        objEmbeddingModel = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        if self.boolCreateDatabase:
            objLoader = DirectoryLoader(
                strInjestPath,
                glob = "**/*.txt",
                loader_cls = TextLoader,
                show_progress = False)
            strRawDocuments = objLoader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            strDocuments = text_splitter.split_documents(strRawDocuments)
            db = Chroma.from_documents(strDocuments, objEmbeddingModel, persist_directory = strInjestPath + "/chroma_embeddings")
            return db
        else:
            db = Chroma(embedding_function = objEmbeddingModel, persist_directory = strInjestPath + "/chroma_embeddings")
            return db
        
    def get_response(self, strQuestion, strOutputPath = None):
        # Retrieve relevant documents based on the question
        objResponseRetriever = self.objRetriever.get_relevant_documents(strQuestion)
        intMaxRetry = 3
        intTry = 0
        while intTry != intMaxRetry:
            intTry = intTry + 1
            try:
                response = self.objChain.invoke(strQuestion)
                response_content = response.content
                break
            except AttributeError as e:
                response_content = self.objChain.invoke(strQuestion)
                break
            except Exception as e:
                time.sleep(90)
                print("Error on get_response(): ",e)
        if strOutputPath:
            current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = uuid.uuid4()
            output_file_path = os.path.join(strOutputPath, f'LLMSetting_1_response_{current_datetime}_{unique_id}.txt')
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(response_content)
        if strOutputPath:
            current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = uuid.uuid4()
            output_file_path = os.path.join(strOutputPath, f'LLMSetting_1_response_{current_datetime}_{unique_id}.txt')
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(response_content)

        return objResponseRetriever, response_content