import os
from dotenv import load_dotenv
load_dotenv()
import Large_Language_Model.LLM_Component as LLM_Component
import Large_Language_Model.Personas as Personas
strPromptTemplate = Personas.strPersonaUWU + Personas.strDefaultConversationTemplate 

objLLM = LLM_Component.LLM(intLLMSetting = 1,
                           strIngestPath = 'Knowledge_Base',
                           strPromptTemplate = strPromptTemplate,
                           strAPIKey = os.getenv('GROQ_KEY'),
                           boolCreateDatabase = True)
strResponse = objLLM.get_response('Hi what is your name',boolVerbose=True)[0]
print(strResponse)

strResponse = objLLM.get_response('Show the email template',boolVerbose=True)[0]
print(strResponse)