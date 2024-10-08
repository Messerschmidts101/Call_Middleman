import json
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import Large_Language_Model.LLM_Component as LLM_Component
import Large_Language_Model.Personas as Personas
objLLM = LLM_Component.LLM(intLLMSetting = 1,
                           strIngestPath = 'Website/Database/Main_Knowledge_Base',
                           strPromptTemplate =  Personas.strTemplateSuggestResponse,
                           strAPIKey = os.getenv('GROQ_KEY'),
                           boolCreateDatabase = False)
tblSamples = pd.read_csv('call_scripts_inchcape.csv')
dictResults = {
    'Type':[],
    'Topic':[],
    'Original':[],
    'Suggested_Response':[]
}

for index, rowRow in tblSamples.iterrows():
    strResponse, strSource = objLLM.get_response(rowRow['Message'],boolVerbose=True)
    print("Script: ",rowRow['Message'],"\nResponse: ",strResponse)
    dictResults['Type'].append(rowRow['Type'])
    dictResults['Topic'].append(rowRow['Topic'])
    dictResults['Original'].append(rowRow['Message'])
    dictResults['Suggested_Response'].append(strResponse)

results_df = pd.DataFrame(dictResults)
results_df.to_csv('test_results/suggested_response_scripts.csv', index=False)