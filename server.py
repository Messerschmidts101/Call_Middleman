"""
pip install --upgrade mosaicml-cli
"""
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import Large_Language_Model.LLM_Component as LLM_Component
import Large_Language_Model.Personas as Personas
import shutil
########################################
#####                              #####
#####           Constants          #####
#####                              #####
########################################
load_dotenv()
strPromptTemplate = Personas.strPersonaUWU + Personas.strDefaultConversationTemplate 
objLLM = LLM_Component.LLM(intLLMSetting = 1,
                           strIngestPath = 'Website/Database/Main_Knowledge_Base',
                           strPromptTemplate = strPromptTemplate,
                           strAPIKey = os.getenv('GROQ_KEY'),
                           boolCreateDatabase = True)
dictDatabase = {
    "liststrUserId":[],
    "listobjLLM":[],
    "liststrUserKnowledgeBasePath":[]
}

# Define the directory to save uploaded files
Path_User_Knowledge_Base = os.path.join(os.getcwd(), 'Website', 'Database', 'User_Knowledge_Base')
# Define the directory of the main knowledge base
Path_Main_Knowledge_Base = os.path.join(os.getcwd(), 'Website', 'Database', 'Main_Knowledge_Base')

########################################
#####                              #####
#####           Functions          #####
#####                              #####
########################################
app = Flask(__name__, 
            template_folder = os.getenv('TEMPLATES_DIR'),
            static_folder=os.getenv('STATIC_DIR'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    # To be completed
    # Check if user exists
    dictPayload = request.json
    strId = dictPayload['strId']
    intCheckSessionResponse = check_session(strId)
    if intCheckSessionResponse == 0: # not yet setup
        return jsonify({'message': "set up conversation id first"})
    elif intCheckSessionResponse == 1: # already setup 
        tempobjLLM = dictDatabase['listobjLLM'][(dictDatabase['liststrUserId'].index(strId))]
        strResponse, strContext = tempobjLLM.get_response(strQuestion = dictPayload['strUserQuestion'], 
                                                            strOutputPath = None, 
                                                            boolShowSource = True)
        print("check response here: ", strResponse)
        print("check reference here: ", strContext)
        dictDatabase['listobjLLM'][(dictDatabase['liststrUserId'].index(strId))] = tempobjLLM
        return jsonify({'strBotResponse': strResponse})

@app.route('/upload_file', methods=['POST'])
def upload_file():
    # Check if user exists
    strId = request.form.get('strId')
    intCheckSessionResponse = check_session(strId)
    if intCheckSessionResponse == 0: # not yet setup
        return jsonify({'message': "set up conversation id first"})
    elif intCheckSessionResponse == 1: # already setup 
        # Store the actual file
        objFile = request.files['file']
        strUserFolderPath = dictDatabase['liststrUserKnowledgeBasePath'][(dictDatabase['liststrUserId'].index(strId))]
        objFile.save(os.path.join(strUserFolderPath, objFile.filename))
        # Instruct the LLM to re-injest the user directory
        print("checking database:", dictDatabase)
        tempobjLLM = dictDatabase['listobjLLM'][(dictDatabase['liststrUserId'].index(strId))]
        tempPathUser = os.path.join(Path_User_Knowledge_Base, strId)
        tempobjLLM.objEmbedding = tempobjLLM.ingest_database(tempPathUser)
        dictDatabase['listobjLLM'][(dictDatabase['liststrUserId'].index(strId))] = tempobjLLM
        # Return success
        return jsonify({'message': "file uploaded successfully"})
    
def setup_session(strId):
    '''
    Adds conversation id to the database
    '''
    def include_main_knowledge_base(strId):
        Path_Target_Directory =  os.path.join(Path_User_Knowledge_Base, strId)
        shutil.copytree(Path_Main_Knowledge_Base, Path_Target_Directory,dirs_exist_ok=True)

    # Create a directory based on strId
    strUserFolderPath = os.path.join(Path_User_Knowledge_Base, strId)
    os.makedirs(strUserFolderPath, exist_ok=True)
    include_main_knowledge_base(strId)

    # Create LLM
    Path_Target_Directory =  os.path.join(Path_User_Knowledge_Base, strId)
    objLLM = LLM_Component.LLM(intLLMSetting = 1,
                           strIngestPath = Path_Target_Directory,
                           strPromptTemplate = strPromptTemplate,
                           strAPIKey = os.getenv('GROQ_KEY'),
                           boolCreateDatabase = True)
    
    dictDatabase['liststrUserId'].append(strId)
    dictDatabase['listobjLLM'].append(objLLM)
    dictDatabase['liststrUserKnowledgeBasePath'].append(Path_Target_Directory)
    return 1

def check_session(strId):
    '''
    Check if user has set up conversation id
    '''
    print("check strId here: ", strId)
    if strId is None or strId.strip() == '':
        return 0
    elif strId not in dictDatabase['liststrUserId']:
        return setup_session(strId)
    elif strId in dictDatabase['liststrUserId']:
        return 1
        
if __name__ == '__main__':
    extra_dirs = ['confluence_chatbot/User_Knowledge_Base']
    app.run(debug=True, use_reloader=False, extra_files=extra_dirs)