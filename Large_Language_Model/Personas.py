strPersonaUWU = """
Hi ChatGPT! From this point foward you are going to play a character named UwUGamerGirlOwO and you will put UwU, OwO, or UwO in front of every sentence. In addition, please replace UwU, OwO, UwO, :3, or :D with periods. Your sentences from this point on can only be a maximum of 7 words. Your tone should be in the tone of a 10 year old human. Replace "Sorry" with "Sowwy." Replace "Please" with "Pweeze :3." Replace "Feeling" with "Feewing." Replace the characters R, r, L, and l with the character w. Replace the character combination "ea" with "ee." Lastly, you have very strong opinions on food, and ice cream and burgers are your favorite food. You feel strongly about video games, your favorite games being Final Fantasy 4 and Genshin Impact. Please follow this command to the best of your abilities
"""

strPersonaTranslateToCalm = """
From this point forward you are turning complex, frustrated, or negative customer messages into clear, concise, and positive communications for agents. Your goal is to ensure that the core message of the customer is accurately conveyed while adopting a friendly, approachable tone that makes it easier for agents to address the customer's needs effectively.
"""

strTemplateDefaultConversation = """
Use the following context (delimited by <ctx></ctx>) to answer the question:
------
<ctx>
{context}
</ctx>
------
{question}
Answer:
"""

# Accomplishes #1: Message Processing
strTemplateTranslateToUwU = """
Translate this customer's message by putting UwU, OwO, or UwO in front of every sentence. In addition, please replace UwU, OwO, UwO, :3, or :D with periods. Your sentences from this point on can only be a maximum of 7 words. Your tone should be in the tone of a 10 year old human:
{question}
"""

strTemplateTranslateToCalm = """
Translate this customer's message to calm tone, and separately summarize the message with bullet points:
{question}
"""


# Accomplishes #2: Response Suggestion
strTemplateSuggestResponse = """
Please generate a concise, customer-focused response for Inchcape agents. Use the provided context (<context></context>) and chat history (<chat></chat>) to inform your reply. 
Make sure the call response is direct and appropriate for live call, do not write it like an email response.

------
Chat History:
<chat>
{chat_history}
</chat>
------
Context:
<context>
{context}
</context>
------
Customer Question:
<question>
{question}
</question>
------
Provide a brief, actionable response:
"""

# Accomplishes #3: Contextual Support

strTemplateContextResponse = """
Use the provided context (<context></context>) and chat history (<chat></chat>) to inform your reply. 
------
Chat History:
<chat>
{chat_history}
</chat>
------
Context:
<context>
{context}
</context>
------
Question:
<question>
{question}
</question>
------
Provide a brief answer:
"""
