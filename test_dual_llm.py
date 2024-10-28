import os
import utils as U
from dotenv import load_dotenv
load_dotenv()

objLLM = U.create_llm_to_room(tblContextDatabase = None,
                                strRoom = 'test_dual_llm',
                                strPathKnowledgeBaseUser = 'Website/Database/User_Knowledge_Base',
                                strPathKnowledgeBaseMain = 'Website/Database/Main_Knowledge_Base')

print(objLLM.get_response('Hi my name is Bryan Ferrer, my birth year is 2000',boolVerbose = True))
print(objLLM.get_response('Explain STD-01',boolVerbose = True))
print(objLLM.get_response('What is my name and birth year',boolVerbose = True))