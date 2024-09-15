import os
from dotenv import load_dotenv
load_dotenv()
import Large_Language_Model.LLM_Component as LLM_Component
import Large_Language_Model.Personas as Personas
#strPromptTemplate = Personas.strPersonaUWU + Personas.strTemplateDefaultConversation 

objLLM = LLM_Component.LLM(intLLMSetting = 1,
                           strIngestPath = 'Website/Database/Main_Knowledge_Base',
                           strPromptTemplate = Personas.strTemplateSuggestResponse,
                           strAPIKey = os.getenv('GROQ_KEY'),
                           boolCreateDatabase = False,
                           intLLMAccessory = 3)
strResponse = objLLM.get_response('Hi my name is Das',boolVerbose=True)[0]
print(strResponse)

strResponse = objLLM.get_response('What is my name?',boolVerbose=True)[0]
print(strResponse)

strResponse = objLLM.get_response('What is the warranty code for extended warranty',boolVerbose=True)[0]
print(strResponse)