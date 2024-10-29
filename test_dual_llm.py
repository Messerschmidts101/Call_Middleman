import os
import utils as U
import Large_Language_Model.Personas as Personas
from dotenv import load_dotenv
load_dotenv()
"""
##########################################
#####                                #####
#####           NORMAL LLM           #####
#####                                #####
##########################################

objLLM1 = U.create_llm_to_room(tblContextDatabase = None,
                                strRoom = 'test_dual_llm',
                                strPathKnowledgeBaseUser = 'Website/Database/User_Knowledge_Base',
                                strPathKnowledgeBaseMain = 'Website/Database/Main_Knowledge_Base')
print(objLLM1.get_response('Hi my name is Bryan Ferrer, my birth year is 2000',boolVerbose = True))
print(objLLM1.get_response('Explain STD-01',boolVerbose = True))
print(objLLM1.get_response('What is my name and birth year',boolVerbose = True))"""

##########################################
#####                                #####
#####          Advisor LLM           #####
#####                                #####
##########################################

objLLM2 = U.create_llm_to_room(tblContextDatabase = None,
                                strRoom = 'test_dual_llm',
                                strPathKnowledgeBaseUser = 'Website/Database/User_Knowledge_Base',
                                strPathKnowledgeBaseMain = 'Website/Database/Main_Knowledge_Base',
                                intLLMSetting = 1,
                                intLLMAccessory = 4,
                                strPromptTemplate = Personas.strTemplateQAResponse)

# Yes because within protocol
print(objLLM2.get_QA(strCustomerQuestion="hello alfonso i have a problem regarding my invoice not being not using my warranty that's all my name is brian by the way and my last service was on november 2 2024",
                     strAgentResponse="Hello Brian, I understand how frustrating this must be. To help you, I need the invoice code and details of your last service on November 2, 2024. I will also validate your warranty. Once I have these details, I can identify the issue and provide a resolution"))

# No because the response is not within protocol
print(objLLM2.get_QA(strCustomerQuestion="hello alfonso i have a problem regarding my invoice not being not using my warranty that's all my name is brian by the way and my last service was on november 2 2024",
                     strAgentResponse="Hello Brian, may i know what is the distance of your house to our service branch?"))

# No because the response is skips steps within protocol
print(objLLM2.get_QA(strCustomerQuestion="my warranty is STD-01 and my mileage is just 59,000 but my receipt didnt use my warranty to reduce the cost",
                     strAgentResponse="Since you only have STD-01 which is the Standard Warranty it only covers labor for up to 3 years or 36,000 miles, may we offer you EXT-02 which is our Extended Warranty and covers labor for up to 60,000 miles."))

# Yes because within protocol
print(objLLM2.get_QA(strCustomerQuestion="since my warranty is STD-01 and my mileage is already beyond 36,000 miles, what do you think i should do?",
                     strAgentResponse="Since you only have STD-01 which is the Standard Warranty it only covers labor for up to 3 years or 36,000 miles, may we offer you EXT-02 which is our Extended Warranty and covers labor for up to 60,000 miles."))

