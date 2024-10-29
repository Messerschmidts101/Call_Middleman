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
Improve this message to calm tone message (do not write like an email), and separately summarize the message with bullet points:
{question}
"""


# Accomplishes #2: Response Suggestion
strTemplateSuggestResponse = """
Please generate a concise, customer-focused response for Inchcape agents. Use the provided context (<context></context>) and chat history (<chat></chat>) to inform your reply. 
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
Provide a brief, actionable response appropriate for live call, do not write it like an email response:
"""

strTemplateQAResponse = """
This is the conversation history so far:
{chat_history}

This is the recent query of the customer:
{customer_question}

This is the recent response of the agent:
{llm_response}

This is the protocol of the when handling calls:
{context}

Do you think the response of the agent is correct and why? (Yes/No):
"""

["chat_history",
                                     "customer_question",
                                     "response_guide",
                                     "context"]

strTemplateSuggestResponseV2 = """
This is the conversation history so far:
{chat_history}

This is the recent query of the customer:
{customer_question}

This is the protocol of the when handling calls:
{response_guide}

This is additional context regarding the customer's question:
{context}

Provide a brief, actionable response appropriate for live call, do not write it like an email response:
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
Provide a brief answer based on the information above:
"""
