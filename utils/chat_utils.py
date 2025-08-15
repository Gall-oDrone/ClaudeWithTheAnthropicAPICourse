def add_user_message(messages, text):
    user_msg = {"role":"user","content":text}
    messages.append(user_msg)

def add_assistant_message(messages, text):
    assistant_message = {"role":"assistant","content":text}
    messages.append(assistant_message)
