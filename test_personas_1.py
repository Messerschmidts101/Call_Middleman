import json
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import Large_Language_Model.LLM_Component as LLM_Component
import Large_Language_Model.Personas as Personas
objLLM = LLM_Component.LLM(intLLMSetting = 5,
                           strIngestPath = 'Website/Database/User_Knowledge_Base/222BBB',
                           strPromptTemplate =  Personas.strTemplateTranslateToCalm,
                           strAPIKey = os.getenv('GROQ_KEY'),
                           boolCreateDatabase = False)
tblSamples = pd.read_csv('call_scripts.csv')
dictResults = {
    'Type':[],
    'Original':[],
    'Translated':[]
}

for index, rowRow in tblSamples.iterrows():
    strResponse, strSource = objLLM.get_response(rowRow['Message'],boolVerbose=True)
    print("Script: ",rowRow['Message'],"\nResponse: ",strResponse)
    dictResults['Type'].append(rowRow['Type'])
    dictResults['Original'].append(rowRow['Message'])
    dictResults['Translated'].append(strResponse)

results_df = pd.DataFrame(dictResults)
results_df.to_csv('translated_scripts.csv', index=False)