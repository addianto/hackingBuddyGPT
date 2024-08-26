import re

from hackingBuddyGPT.capabilities.capability import capabilities_to_action_model
import openai


class LLMHandler(object):
    """
    LLMHandler is a class responsible for managing interactions with a large language model (LLM).
    It handles the execution of prompts and the management of created objects based on the capabilities.

    Attributes:
        llm (object): The large language model to interact with.
        _capabilities (dict): A dictionary of capabilities that define the actions the LLM can perform.
        created_objects (dict): A dictionary to keep track of created objects by their type.
    """

    def __init__(self, llm, capabilities):
        """
        Initializes the LLMHandler with the specified LLM and capabilities.

        Args:
            llm (object): The large language model to interact with.
            capabilities (dict): A dictionary of capabilities that define the actions the LLM can perform.
        """
        self.llm = llm
        self._capabilities = capabilities
        self.created_objects = {}
        self._re_word_boundaries = re.compile(r'\b')

    def call_llm(self, prompt):
        """
        Calls the LLM with the specified prompt and retrieves the response.

        Args:
            prompt (list): The prompt messages to send to the LLM.

        Returns:
            response (object): The response from the LLM.
        """
        print(f'Initial prompt length: {len(prompt)}')

        def call_model(prompt):
            """ Helper function to avoid redundancy in making the API call. """
            return self.llm.instructor.chat.completions.create_with_completion(
                model=self.llm.model,
                messages=prompt,
                response_model=capabilities_to_action_model(self._capabilities)
            )

        try:
            if len(prompt) > 30:
                return call_model(self.adjust_prompt(prompt))

            return call_model(self.adjust_prompt_based_on_token(prompt))
        except openai.BadRequestError as e:
            print(f'Error: {str(e)} - Adjusting prompt size and retrying.')
            # Reduce prompt size; removing elements and logging this adjustment
            return call_model(self.adjust_prompt_based_on_token(self.adjust_prompt(prompt)))
    def adjust_prompt(self, prompt):
        adjusted_prompt = prompt[len(prompt) - 5 - (len(prompt) % 2): len(prompt)]
        if not isinstance(adjusted_prompt[0], dict):
            adjusted_prompt = prompt[len(prompt) - 5 - (len(prompt) % 2) - 1: len(prompt)]

        print(f'Adjusted prompt length: {len(adjusted_prompt)}')
        print(f'adjusted prompt:{adjusted_prompt}')
        return prompt

    def add_created_object(self, created_object, object_type):
        """
        Adds a created object to the dictionary of created objects, categorized by object type.

        Args:
            created_object (object): The object that was created.
            object_type (str): The type/category of the created object.
        """
        if object_type not in self.created_objects:
            self.created_objects[object_type] = []
        if len(self.created_objects[object_type]) < 7:
            self.created_objects[object_type].append(created_object)

    def get_created_objects(self):
        """
        Retrieves the dictionary of created objects and prints its contents.

        Returns:
            dict: The dictionary of created objects.
        """
        print(f'created_objects: {self.created_objects}')
        return self.created_objects

    def adjust_prompt_based_on_token(self, prompt):
        prompt.reverse()
        tokens = 0
        max_tokens = 10000
        for item in prompt:
            if tokens > max_tokens:
                #if isinstance(item, dict):
                #    tokens = tokens - self.get_num_tokens(item["content"])
                prompt.remove(item)
            else:
                if isinstance(item, dict):
                    new_token_count = (tokens + self.get_num_tokens(item["content"]))
                    if  new_token_count<= max_tokens:
                        tokens = new_token_count
                else:
                    continue

        print(f'tokens:{tokens}')
        prompt.reverse()
        return prompt

    def get_num_tokens(self, content):
        return len(self._re_word_boundaries.findall(content)) >> 1
