import json
from anthropic import Anthropic
from typing import Optional, List, Dict, Any

from utils.chat_utils import text_to_json
from utils.graders import Grader, GradingCriteria, GradingResult


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
    
    def set_stop_sequences(self, stop_sequences: list) -> None:
        """
        Set the stop sequences for the chat request.
        """
        self.params["stop_sequences"] = stop_sequences
    
    def get_stop_sequences(self) -> list:
        """
        Get the current stop sequences for the chat request.
        """
        return self.params["stop_sequences"]
    
    def set_params(self, params: dict) -> None:
        """
        Set the parameters for the chat request.
        """
        self.params = params
    
    def get_params(self) -> dict:
        """
        Get the current parameters for the chat request.
        """
        return self.params
    
    def send_message(self) -> str:
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
    
    def send_message_stream(self, print_stream: bool = True, print_final_message: bool = True) -> tuple[str, str]:
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
    
    def add_user_message(self, messages: list, text: str) -> None:
        """
        Add a user message to the messages list.
        
        Args:
            messages (list): List of message dictionaries.
            text (str): The user's message text.
        """
        user_msg = {"role": "user", "content": text}
        messages.append(user_msg)
    
    def add_assistant_message(self, messages: list, text: str) -> None:
        """
        Add an assistant message to the messages list.
        
        Args:
            messages (list): List of message dictionaries.
            text (str): The assistant's message text.
        """
        assistant_message = {"role": "assistant", "content": text}
        messages.append(assistant_message)

    def generate_dataset(self, prompt: str, text:str, save_path: Optional[str] = None) -> list:
        """
        Generate a dataset of tasks using the Anthropic API.
        """
        self.add_user_message(self.params["messages"], prompt)
        self.add_assistant_message(self.params["messages"], text)
        response = self.send_message()
        dataset = text_to_json(response)
        if save_path:
            with open(save_path, "w") as f:
                json.dump(dataset, f, indent=4)
        return dataset
    
    def run_test_case(self, test_case: Dict[str, str], grader: Optional[Grader] = None) -> Dict[str, Any]:
        """
        Run a single test case evaluation.
        
        Args:
            test_case (Dict[str, str]): Dictionary containing 'prompt' and 'expected_response' keys
            grader (Optional[Grader]): Grader instance to use. If None, creates a new one.
            
        Returns:
            Dict[str, Any]: Test case results including response and grading
        """
        if grader is None:
            grader = Grader()
        
        prompt = test_case.get("prompt", "")
        expected_response = test_case.get("expected_response", "")
        
        # Generate response using the current client
        self.params["messages"] = [{"role": "user", "content": prompt}]
        actual_response = self.send_message()
        
        # Grade the response
        grading_result = grader.grade_comprehensive(prompt, actual_response)
        
        return {
            "test_case": test_case,
            "actual_response": actual_response,
            "grading_results": grading_result,
            "passed": grading_result["model_grader"].passed and grading_result["code_grader"].passed
        }
    
    def run_eval(self, test_dataset: List[Dict[str, str]], 
                 save_results: bool = True, 
                 results_path: str = "eval_results.json",
                 grader: Optional[Grader] = None) -> Dict[str, Any]:
        """
        Run evaluation on a complete test dataset.
        
        Args:
            test_dataset (List[Dict[str, str]]): List of test cases with 'prompt' and 'expected_response'
            save_results (bool): Whether to save results to file
            results_path (str): Path to save evaluation results
            grader (Optional[Grader]): Grader instance to use. If None, creates a new one.
            
        Returns:
            Dict[str, Any]: Complete evaluation results and summary
        """
        if grader is None:
            grader = Grader()
        
        results = []
        passed_count = 0
        
        for i, test_case in enumerate(test_dataset):
            print(f"Running test case {i+1}/{len(test_dataset)}...")
            
            try:
                test_result = self.run_test_case(test_case, grader)
                results.append(test_result)
                
                if test_result["passed"]:
                    passed_count += 1
                    
            except Exception as e:
                print(f"Error in test case {i+1}: {str(e)}")
                results.append({
                    "test_case": test_case,
                    "error": str(e),
                    "passed": False
                })
        
        # Generate summary
        total_tests = len(test_dataset)
        pass_rate = passed_count / total_tests if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_count,
            "failed_tests": total_tests - passed_count,
            "pass_rate": pass_rate,
            "results": results
        }
        
        # Save results if requested
        if save_results:
            with open(results_path, 'w') as f:
                json.dump(summary, f, indent=4)
            print(f"Results saved to {results_path}")
        
        print(f"Evaluation complete: {passed_count}/{total_tests} tests passed ({pass_rate:.2%})")
        
        return summary