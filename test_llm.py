import os
import utils as U
import Large_Language_Model.Personas as Personas
from dotenv import load_dotenv
load_dotenv()
##########################################
#####                                #####
#####           NORMAL LLM           #####
#####                                #####
##########################################

'''objLLM1 = U.create_llm_to_room(tblContextDatabase = None,
                                strRoom = 'test_dual_llm2',
                                strPathKnowledgeBaseUser = 'Website/Database/User_Knowledge_Base',
                                strPathKnowledgeBaseMain = 'Website/Database/Main_Knowledge_Base',
                                intLLMSetting = 1,
                                intLLMAccessory = 5,
                                strPromptTemplate = Personas.strTemplateSuggestResponseV2)
print('====== 1')
print(objLLM1.get_response("hello alfonso i have a problem regarding my invoice not being not using my warranty that's all my name is brian by the way and my last service was on november 2 2024"))
print('====== 2')
print(objLLM1.get_response("my warranty is STD-01 and my mileage is just 59,000 but my receipt didnt use my warranty to reduce the cost"))
print('====== 3')
print(objLLM1.get_response("is there another package to extend my wwarranty and buy it so that it can be covered?"))
print('====== 4')
print(objLLM1.get_response("there is nothing else i need"))'''

objLLM2 = U.create_llm_to_room(tblContextDatabase = None,
                                strRoom = 'test_dual_llm3',
                                strPathKnowledgeBaseUser = 'Website/Database/User_Knowledge_Base',
                                strPathKnowledgeBaseMain = 'Website/Database/Main_Knowledge_Base',
                                intLLMSetting = 1,
                                intLLMAccessory = 5,
                                strPromptTemplate = Personas.strTemplateSuggestResponseV2)
print('====== 1')
print(objLLM2.get_response("hello bryan, it seems like i was charged twice in my bank account after my recent car service in October 1st 2024"))

print('====== 2')
print(objLLM2.get_response("the invoice code is AAA111 for October 1st 2024, and as you can plain as day my there is double amount of deduction"))

'''
print('====== 2')
print(objLLM2.get_response("my warranty is STD-01 and my mileage is just 59,000 but my receipt didnt use my warranty to reduce the cost"))
print('====== 3')
print(objLLM2.get_response("is there another package to extend my wwarranty and buy it so that it can be covered?"))
print('====== 4')
print(objLLM2.get_response("there is nothing else i need"))'''