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
from operator import itemgetter
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
        self.strIngestPath = strIngestPath
        self.objEmbeddingModel = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.lisChatHistory = []
        self.initialize_llm(intLLMSetting,
                            fltTemperature,
                            intRetrieverK,
                            intLLMAccessory,
                            strPromptTemplate)
        
        #===== These starting arguments needed to be class attributes because RAG chain are required to be regenerated when adding new data=====
        self.intLLMAccessory = intLLMAccessory
        self.intRetrieverK = intRetrieverK
        self.intLLMSetting = intLLMSetting
        self.strPromptTemplate = strPromptTemplate

    def initialize_llm(self, intLLMSetting, 
                       fltTemperature, 
                       intRetrieverK,
                       intLLMAccessory,
                       strPromptTemplate):
        '''
        This method creates LLM with their RAG Chain for this class. 
        This LLM allows chat history and context.
        Both chat history and context has retrievers, thus the chain will be recreated per question if the vector database will be updated.
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
        self.create_llm(intLLMSetting = intLLMSetting,
                        fltTemperature = fltTemperature,
                        strModelName = strModelName)
        boolValidity = self.check_validity_of_settings(intLLMAccessory, strPromptTemplate)
        if not boolValidity:
            raise ValueError("Invalid LLM accessory and prompt template combination")
        self.create_chain(intLLMAccessory = intLLMAccessory,
                          intRetrieverK = intRetrieverK,
                          strPromptTemplate = strPromptTemplate)
        
    def create_llm(self,intLLMSetting,fltTemperature,strModelName):
        if intLLMSetting in [1, 2, 5]: # Groq LLM
            if not self.strAPIKey:
                raise ValueError(f"Requires API Key, set value of 'strAPIKey'")
            self.objLLM = ChatGroq(temperature = fltTemperature, 
                                   model_name = strModelName, 
                                   groq_api_key = self.strAPIKey)
        elif intLLMSetting == 3:  # HuggingFace LLM
            self.objLLM = HuggingFaceEndpoint(repo_id = strModelName, 
                                              temperature = fltTemperature, 
                                              token = self.strAPIKey)
        elif intLLMSetting == 4: # OpenAI LLM
            self.objLLM = AzureChatOpenAI(
                api_key = self.strAPIKey,
                deployment_name = strModelName,  # Use your specific deployment name
                model = strModelName,  # Or another model you have deployed
                temperature = fltTemperature,
                api_version = "2024-02-01"
            )

    def create_chain(self,intLLMAccessory,intRetrieverK,strPromptTemplate):
        # intLLMSetting is obsolete
        if intLLMAccessory > 0:
            if intLLMAccessory == 1:
                #just context on RAG
                self.objPromptTemplate = PromptTemplate(template = strPromptTemplate, 
                                                        input_variables = ["context", "question"])
                self.objRetrieverContext = self.ingest_context().as_retriever(search_kwargs={"k": intRetrieverK})
                self.objChain = ({"context": self.objRetrieverContext | self.combine_docs, 
                                  "question": RunnablePassthrough()} | 
                                  self.objPromptTemplate | 
                                  self.objLLM)
            elif intLLMAccessory == 2:
                raise ValueError(f"To be added soon Chat History only LLM accessory: {intLLMAccessory}")
            elif intLLMAccessory == 3:
                # Both context and chat history in RAG
                self.objPromptTemplate = PromptTemplate(
                    template = strPromptTemplate, 
                    input_variables=["context", "question", "chat_history"]
                )
                self.objRetrieverContext = self.ingest_context().as_retriever(search_kwargs={"k": intRetrieverK})
                self.objRetrieverChatHistory = self.ingest_chat_history().as_retriever(search_kwargs={"k": intRetrieverK})
                # Use the updated combine_docs_chat_history function to provide chat history
                self.objChain = ({"context": self.objRetrieverContext | self.combine_docs, 
                                  "chat_history": self.objRetrieverContext | self.combine_docs,  
                                  "question": RunnablePassthrough()} | 
                                  self.objPromptTemplate | 
                                  self.objLLM)
            elif intLLMAccessory == 4:
                # QA mode
                self.objPromptTemplate = PromptTemplate(
                    template = strPromptTemplate, 
                    input_variables=["chat_history","customer_question","llm_response","context"]
                )

                self.objRetrieverContext = self.ingest_context_qa().as_retriever(search_kwargs={"k": intRetrieverK})
                self.objRetrieverChatHistory = self.ingest_chat_history().as_retriever(search_kwargs={"k": intRetrieverK})
                # Use the updated combine_docs_chat_history function to provide chat history
                self.objChain = ({"chat_history":  itemgetter('customer_question') |self.objRetrieverChatHistory | self.combine_docs,  
                                  "context": itemgetter('customer_question') | self.objRetrieverContext | self.combine_docs,
                                  "customer_question": itemgetter('customer_question') | RunnablePassthrough(),
                                  "llm_response": itemgetter('llm_response') | RunnablePassthrough()} | 
                                  self.objPromptTemplate | 
                                  self.objLLM)
                
            else:
                raise ValueError(f"Invalid LLM Additions: {intLLMAccessory}")
        else:
            self.objPromptTemplate = PromptTemplate(template = strPromptTemplate, 
                                                    input_variables=["question"])
            self.objChain = ({"question": RunnablePassthrough()} | 
                            self.objPromptTemplate | 
                            self.objLLM)

    def check_validity_of_ingest_path(self,strIngestPath):
        print('before replace: ', strIngestPath)
        strIngestPath = strIngestPath.replace("\\", " ").replace("/", " ")
        print('after replace: ', strIngestPath)
        lisstrIngestPath = list(strIngestPath.split(" "))
        print('list path: ', lisstrIngestPath)
        strIngestPath = os.path.join(*lisstrIngestPath)
        print('new path: ', strIngestPath)
        return strIngestPath
    
    def check_validity_of_settings(self,intLLMAccessory,strPromptTemplate):
        if 'chat_history' in strPromptTemplate and intLLMAccessory in [2,3,4]:
            return True
        elif 'chat_history' not in strPromptTemplate and intLLMAccessory not in [2,3,4]:
            return True
        else:
            return False

    def combine_docs(self, docs):
        '''
        This method is a sub process for ingesting database for context only RAG chains, triggered by ingest_context()
        '''
        return "\n\n".join(doc.page_content for doc in docs)

    def add_chat_history(self, strUserInput, strLLMOutput):
        '''
        This method does actually adds chat to the history for this LLM, however the chain is regenerated because the history retriever needs to be updated back to the chain.
        '''
        # Update chat history with both User input and System output in the same dictionary
        self.lisChatHistory.append({"Message Index":len(self.lisChatHistory)+1,
                                    "Timestamp": datetime.now(), 
                                    "User": strUserInput, 
                                    "System": strLLMOutput})
        
        # Update vector database of chat history
        # WRONGGGGG code below will not work as the retriever wont be updated to the RAG chain; solution is recreate the chain
        # objEmbeddingChatHistory = self.ingest_chat_history()
        # self.objRetrieverChatHistory = objEmbeddingChatHistory.as_retriever(search_kwargs={"k": 5})
        self.create_chain(self.intLLMAccessory,self.intRetrieverK,self.strPromptTemplate)
    
    def add_context(self):
        '''
        This method does actually adds context for this LLM, however the chain is regenerated because the context retriever needs to be updated back to the chain.
        '''
        self.create_chain(self.intLLMAccessory,self.intRetrieverK,self.strPromptTemplate)

    def ingest_context_qa(self):
        strContextKnowledgeDirectory = os.path.join(self.strIngestPath,'chroma_embeddings_qa')
        objLoader = DirectoryLoader(self.strIngestPath, glob="**/agent_playbook.txt", loader_cls=TextLoader, show_progress=False)
        raw_documents = objLoader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = text_splitter.split_documents(raw_documents)
        return Chroma.from_documents(documents, self.objEmbeddingModel, persist_directory = strContextKnowledgeDirectory)

    def ingest_context(self):
        strContextKnowledgeDirectory = os.path.join(self.strIngestPath,'chroma_embeddings')
        objLoader = DirectoryLoader(self.strIngestPath, glob="**/*.txt", loader_cls=TextLoader, show_progress=False)
        raw_documents = objLoader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = text_splitter.split_documents(raw_documents)
        return Chroma.from_documents(documents, self.objEmbeddingModel, persist_directory = strContextKnowledgeDirectory)
        
    def ingest_chat_history(self):
        '''
        This method adds a single dictionary with both User input and System (LLM) output to the chat history and saves it as a text file in the specified folder.
        '''
        #Step one: write conversation as text file
        strChatHistoryRawDirectory = os.path.join(self.strIngestPath, 'chat_folder')
        os.makedirs(strChatHistoryRawDirectory, exist_ok=True)
        strChatHistoryFile = os.path.join(strChatHistoryRawDirectory,'chat_history.txt')
        with open(strChatHistoryFile, 'w') as file:
            file.write('Conversation History')
            for dicItem in self.lisChatHistory:
                file.write(f"-----\nMessage Index: {dicItem["Message Index"]}; Time: {dicItem["Timestamp"]}\nUser: {dicItem["User"]}:\n")
                file.write(f"-----\nMessage Index: {dicItem["Message Index"]}; Time: {dicItem["Timestamp"]}\nSystem: {dicItem["System"]}:\n")
        
        #Step two: embed the text file
        strChatHistoryKnowledgeDirectory = os.path.join(strChatHistoryRawDirectory, 'chroma_embeddings')
        
        print('check path context: ',strChatHistoryKnowledgeDirectory)
        objLoader = DirectoryLoader(strChatHistoryRawDirectory, glob="**/*.txt", loader_cls=TextLoader, show_progress=False)
        raw_documents = objLoader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap=100)
        documents = text_splitter.split_documents(raw_documents)
        return Chroma.from_documents(documents, self.objEmbeddingModel, persist_directory=strChatHistoryKnowledgeDirectory)

    def get_QA(self,strAgentResponse,strCustomerQuestion):
        dicPayload = {
            'llm_response':strAgentResponse,
            'customer_question':strCustomerQuestion
        }
        try:
            print(f'[[VERBOSE]] BEFORE CHAIN:\n{strAgentResponse}\n=====\n{strCustomerQuestion}')
            strResponse = self.objChain.invoke(dicPayload)
            return strResponse.content
        except AttributeError:
            return self.objChain.invoke(dicPayload)
        except Exception as e:
            print('[[VERBOSE]] QA ERROR: ',e)
            
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
            strContexts = self.objRetrieverContext.get_relevant_documents(strQuestion)
        else:
            strContexts = None
        strResponse = self.retry_chain_invoke(strQuestion,intRetries,intDelay,boolVerbose)
        if self.intLLMAccessory in [2,3]:
            self.add_chat_history(strQuestion,strResponse)
            strResult = self.objRetrieverChatHistory.get_relevant_documents(query = strQuestion)
            if boolVerbose:
                print('\n-----','Verbose || Chat History: ',strResult ,'\n-----')
        if strOutputPath:
            self.save_response_as_file(strResponse, strOutputPath)
        return strResponse,strContexts

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

    def save_response_as_file(self, strResponse, strOutputPath):
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4()
        output_file_path = os.path.join(strOutputPath, f'LLM_response_{current_datetime}_{unique_id}.txt')
        
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(strResponse)