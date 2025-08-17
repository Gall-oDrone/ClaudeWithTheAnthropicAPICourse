from anthropic import Anthropic
from typing import Optional


class AnthropicClient:
    """
    A wrapper class for Anthropic API client with default configuration.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-0"):
        """
        Initialize the Anthropic client.
        
        Args:
            api_key (Optional[str]): API key for Anthropic. If None, will use environment variable.
            model (str): Model to use for requests. Defaults to "claude-sonnet-4-0".
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def get_client(self):
        """
        Get the Anthropic client instance.
        
        Returns:
            Anthropic: The Anthropic client instance.
        """
        return self.client
    
    def get_model(self):
        """
        Get the current model name.
        
        Returns:
            str: The current model name.
        """
        return self.model
    
    def set_model(self, model: str):
        """
        Set a new model name.
        
        Args:
            model (str): The new model name to use.
        """
        self.model = model


class ChatClient(AnthropicClient):
    """
    A chat-specific client that extends AnthropicClient with chat functionality.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-0", params: dict = None):
        """
        Initialize the Chat client.
        
        Args:
            api_key (Optional[str]): API key for Anthropic. If None, will use environment variable.
            model (str): Model to use for requests. Defaults to "claude-sonnet-4-0".
            system (str): System message to define the assistant's behavior.
        """
        super().__init__(api_key=api_key, model=model)
        self.params = params
    
    def set_system(self, system: str):
        """
        Set or update the system message.
        
        Args:
            system (str): The system message to define assistant behavior.
        """
        if system:
            self.params["system"] = system
    
    def get_system(self):
        """
        Get the current system message.
        
        Returns:
            str: The current system message.
        """
        return self.params["system"]
    
    def set_max_tokens(self, max_tokens: int):
        """
        Set the maximum number of tokens to generate.
        """
        self.params["max_tokens"] = max_tokens
    
    def get_max_tokens(self):
        """
        Get the current maximum number of tokens to generate.
        """
        return self.params["max_tokens"]
    
    def set_temperature(self, temperature: float):
        """
        Set the temperature for the chat request.
        """
        self.params["temperature"] = temperature
    
    def get_temperature(self):
        """
        Get the current temperature for the chat request.
        """
        return self.params["temperature"]
    
    def set_messages(self, messages: list):
        """
        Set the messages for the chat request.
        """
        self.params["messages"] = messages
    
    def get_messages(self):
        """
        Get the current messages for the chat request.
        """
        return self.params["messages"]
    
    def set_params(self, params: dict):
        """
        Set the parameters for the chat request.
        """
        self.params = params
    
    def get_params(self):
        """
        Get the current parameters for the chat request.
        """
        return self.params
    
    def send_message(self):
        """
        Send a chat request to the Anthropic API.
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content' keys.
            max_tokens (int): Maximum number of tokens to generate. Defaults to 1000.
            
        Returns:
            str: The text content of the assistant's response.
        """
        message = self.client.messages.create(
            model=self.model,
            **self.params
        )
        return message.content[0].text
    
    def send_message_stream(self, print_stream=True, print_final_message=True):
        """
        Send a streaming chat request to the Anthropic API.
        
        Args:
            print_stream (bool): Whether to print the streamed text. Defaults to True.
            
        Returns:
            tuple: (streamed_text, final_message) where streamed_text is the concatenated
                   streamed response and final_message is the complete message object.
        """
        streamed_text = ""
        
        with self.client.messages.stream(
            model=self.model,
            **self.params
        ) as stream:
            for text in stream.text_stream:
                streamed_text += text
                if print_stream:
                    print(text, end="")
            
            final_message = stream.get_final_message()
            if print_final_message:
                print(final_message.content[0].text)
        
        return streamed_text, final_message
    
    def add_user_message(self, messages, text):
        """
        Add a user message to the messages list.
        
        Args:
            messages (list): List of message dictionaries.
            text (str): The user's message text.
        """
        user_msg = {"role": "user", "content": text}
        messages.append(user_msg)
    
    def add_assistant_message(self, messages, text):
        """
        Add an assistant message to the messages list.
        
        Args:
            messages (list): List of message dictionaries.
            text (str): The assistant's message text.
        """
        assistant_message = {"role": "assistant", "content": text}
        messages.append(assistant_message)