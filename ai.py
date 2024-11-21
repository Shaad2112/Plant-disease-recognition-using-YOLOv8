import openai
openai.api_key="sk-abcdef1234567890abcdef1234567890abcdef12"

def chat_with_gpt(prompt):
    response=openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        message=[{"role":"user","content":prompt}]
    )
    return response.choices[0].message.content.script()
if __name__ =="__main__":
    while True:
        user_input =input("you:")
        if user_input.lower() in ["quit", "exit", "bye"]:
            break

        response= chat_with_gpt(user_input)
        print("Chatbot: ", response)
