# Call_Middleman
A middleman solution for call centers that facilitates communication between agents and customers. This tool filters, summarizes, and enhances messages, helping to reduce cognitive load and emotional stress for call center agents. By streamlining interactions, it improves both the mental well-being of agents and their overall work effectiveness.

## Benefits
1. **Improves Worker's Mental Health**: Alleviates emotional strain and stress for agents by managing challenging customer interactions more effectively.
2. **Promote Inclusive Call Center Work**: Makes the job easier for both younger and older workers by reducing the complexity of handling customer interactions, thus supporting a diverse workforce and helping to create inclusive job opportunities.
3. **Boost Call Productivity**: Optimizes message exchange, enabling agents to respond to customer queries with greater speed and accuracy.

## How
1. **Message Processing**: A seperate RAG chain translates customer messages, supporting worker mental health by providing clear, actionable points.
2. **Response Suggestions**: Another seperate context-aware RAG chain delivers response suggestions, fostering inclusivity by making the call process easier to navigate.
3. **Contextual Support**: Same latter RAG chain streamlines call flow even lengthy ones, achieving higher productivity and efficiency.

# Requirements
## Install FFMPEG for server; this is used to convert audio files for speech recognition compatability
1. Download full build https://github.com/GyanD/codexffmpeg/releases/tag/2024-10-21-git-baa23e40c1
2. Extract file
3. Add .exe to PATH variable
## Running VENV using Powershell
1. python -m venv venv
2. Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
3. venv\Scripts\activate
## If missing .dll problem, follow this installation 
https://discuss.pytorch.org/t/failed-to-import-pytorch-fbgemm-dll-or-one-of-its-dependencies-is-missing/201969/17
## If problem with chromadb, follow this installation/selection
https://www.scivision.dev/python-windows-visual-c-14-required
## If text to speech not working in browser, add this extension if chrome-based browser
https://chromewebstore.google.com/detail/speech-recognition-anywhe/kdnnmhpmcakdilnofmllgcigkibjonof?pli=1
