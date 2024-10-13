from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from dotenv import load_dotenv
from datetime import datetime
import Large_Language_Model.LLM_Component as LLM_Component
import Large_Language_Model.Personas as Personas
import pandas as pd
import os,shutil
import utils as U
#python test_personas_3.py
load_dotenv()
strPathKnowledgeBaseUser = U.create_knowledge_base_path(0)
strPathKnowledgeBaseMain = U.create_knowledge_base_path(1)
tblContext = U.create_context_table()
tblContext = U.create_llm_to_room(tblContextDatabase = tblContext,
                                    strRoom = "Dummy",
                                    strPathKnowledgeBaseUser = strPathKnowledgeBaseUser,
                                    strPathKnowledgeBaseMain = strPathKnowledgeBaseMain )
objLLM1 = tblContext['objLLM'].iloc[0]

############ Persona 1 ############

strQuestion = "I have a fucking problem regarding the receipt not including my warranty STD-01."
strResponse, strContext = objLLM1.get_response(strQuestion = strQuestion, 
                                                strOutputPath = None, 
                                                boolShowSource = True)
print(f'LLM 1 Response: {strResponse}')



############ Persona 2 ############
strQuestion = "I have a fucking problem regarding the receipt not including my warranty STD-01."
strPromptTemplate = Personas.strTemplateTranslateToCalm
objLLM1.create_chain(intLLMAccessory = 0,
                     intRetrieverK = None,
                     intLLMSetting = 1,
                     strPromptTemplate = strPromptTemplate)
print(f'check template of persona 2 {objLLM1.objPromptTemplate.template}')  # This will print the current prompt template string

strResponse, strContext = objLLM1.get_response(strQuestion = strQuestion, 
                                                strOutputPath = None, 
                                                boolShowSource = True)
print(f'LLM 2 Response: {strResponse}')



############ Persona 3 ############
strQuestion = "Why did my receipt not including my warranty STD-01."
strPromptTemplate = Personas.strTemplateSuggestResponse
objLLM1.create_chain(intLLMAccessory = 3,
                     intRetrieverK = 5,
                     intLLMSetting = 1,
                     strPromptTemplate = strPromptTemplate)
strResponse, strContext = objLLM1.get_response(strQuestion = strQuestion, 
                                                strOutputPath = None, 
                                                boolShowSource = True)
print(f'LLM 3 Response: {strResponse}')