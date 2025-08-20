import json

def add_user_message(messages, text):
    user_msg = {"role":"user","content":text}
    messages.append(user_msg)

def add_assistant_message(messages, text):
    assistant_message = {"role":"assistant","content":text}
    messages.append(assistant_message)

def text_to_json(text):
    """
    Convert text input to JSON formatted output.
    
    Args:
        text (str): The input text to convert to JSON.
    
    Returns:
        dict: The parsed JSON object.
    
    Raises:
        json.JSONDecodeError: If the text cannot be parsed as valid JSON.
    """
    return json.loads(text.strip())
