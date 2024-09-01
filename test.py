import os
from dotenv import load_dotenv
load_dotenv()
import Large_Language_Model.LLM_Component as LLM_Component
import Large_Language_Model.Personas as Personas
strPromptTemplate = Personas.strPersonaUWU + Personas.strDefaultConversationTemplate 


objLLM = LLM_Component.LLM(1,os.getenv('GROQ_KEY'),'Knowledge_Base',strPromptTemplate,True)
strResponse = objLLM.get_response('Hi what is your name')[1]
print(strResponse)

strResponse = objLLM.get_response('Explain retention process to me')[1]
print(strResponse)