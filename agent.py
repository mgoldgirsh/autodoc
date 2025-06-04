from langchain.chat_models import init_chat_model
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

class AutodocLLMAgent(): 
    """ Creates an OpenAI compliant LLM agent """

    def __init__(self, config: dict) -> 'AutodocLLMAgent':
        """Initializes an audodoc llm agent based on `config.json` in the repository structure.

        Args: 
            config (dict): a configuration dictionary to use when creating the autodoc agent

        Returns:
            AutodocLLMAgent: the created autodoc llm agent
        """

        # load the LLM model parameters
        self.model: str = config['llm_model'].lower()
        self.provider: str = config['llm_provider'].lower()
        self.baseurl: str = config['llm_baseurl'].lower()

        # Initialize the model
        if self.provider == "ollama":
            self.llm: BaseChatModel = ChatOllama(base_url=self.baseurl, model=self.model, num_ctx=16384) 
        else:
            # REMEMBER to make sure your api key is set before running
            self.llm: BaseChatModel = init_chat_model(self.model, provider=self.provider)  # see https://python.langchain.com/docs/integrations/chat/ for all providers

    def _summarize_file_system_prompt(self) -> str: 
        return """
        You are a professional software engineer. You can quickly understand the essential parts of files that are required to build software.
        You are given a file in the following markdown format: 
        `filename`:
        ```
        file contents ... 
        ```

        Based off the file markdown. Write down the most important components of this file. Your summary should be written in markdown format so that it can be used in README.md file. 
        The summary should at most 5 major bullet points describing the most important features of the file. Do NOT include any code in your summary simply describe what each file in the directory does. 

        Example of Flow:

        Given the Following File 
        `main.py`:
        ```
        import utils

        if __name__ == "__main__":
            utils.spin_up()
            print("hello world")
        ```
            
        A Valid Output would look like
        - the main module uses the utils module to spin up some processes
        - after spin up the main prints "hello world"

        """.strip()

    def _summarize_directory_system_prompt(self) -> str: 
        return """
        You are a professional software engineer. You can quickly understand code files and other files that are required to build software.
        You are given a README.md file for a specified directory

        Your goal is to generate a ONE SENTENCE description of the directory readme file, that captures the essence of all the files in the directory.
        The generated sentence should be in plaintext and capturing the essence of the directory. 

        """.strip()

    def summarize_file(self, file_contents: str) -> str:
        """Summarizes the file with an openai compliant llm.

        Args:
            file_contents (str): the file contents to summarize 

        Returns:
            str: the llm generated string which represents the summary of the given file
        """

        response = self.llm.invoke([
            SystemMessage(content=self._summarize_file_system_prompt()),
            HumanMessage(content=file_contents)
        ])
        return response.content

    def summarize_directory(self, directory_readme: str) -> str: 
        """Sumamrizes the directory from the directory readme with an openai llm. 

        Args:
            directory_readme (str): the directory readme contents to summarize.

        Returns:
            str: the llm generated summary from the directory readme
        """

        response = self.llm.invoke([
            SystemMessage(content=self._summarize_directory_system_prompt()),
            HumanMessage(content=directory_readme)
        ])
        return response.content
