import os
import utils as U
import Large_Language_Model.Personas as Personas
from dotenv import load_dotenv
load_dotenv()

objLLM2 = U.create_llm_to_room(tblContextDatabase = None,
                                strRoom = 'test_dual_llm',
                                strPathKnowledgeBaseUser = 'Website/Database/User_Knowledge_Base',
                                strPathKnowledgeBaseMain = 'Website/Database/Main_Knowledge_Base',
                                intLLMSetting = 1,
                                intLLMAccessory = 4,
                                strPromptTemplate = Personas.strTemplateQAResponse)

'''print(objLLM.get_response('Hi my name is Bryan Ferrer, my birth year is 2000',boolVerbose = True))
print(objLLM.get_response('Explain STD-01',boolVerbose = True))
print(objLLM.get_response('What is my name and birth year',boolVerbose = True))'''

print(objLLM2.get_QA(strAgentResponse="Hello Brian, I understand how frustrating this must be. To help you, I need the invoice code and details of your last service on November 2, 2024. I will also validate your warranty. Once I have these details, I can identify the issue and provide a resolution",
                    strCustomerQuestion="hello google i have a problem regarding my invoice not being not using my warranty that's all my name is brian by the way and my last service was on november 2 2024"))


objLLM1 = U.create_llm_to_room(tblContextDatabase = None,
                                strRoom = 'test_dual_llm',
                                strPathKnowledgeBaseUser = 'Website/Database/User_Knowledge_Base',
                                strPathKnowledgeBaseMain = 'Website/Database/Main_Knowledge_Base')
print(objLLM1.get_response('Hi my name is Bryan Ferrer, my birth year is 2000',boolVerbose = True))
print(objLLM1.get_response('Explain STD-01',boolVerbose = True))
print(objLLM1.get_response('What is my name and birth year',boolVerbose = True))
