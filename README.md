> User Notes: \
> this file was generated with `autodoc` !!! \
> to use, clone the repo, install requirements, and run `python3 main.py` \
> Demo: 
![demo.mp4](Demo)

# Overall Summary: autodocs

## File Summary: config.py
**config.py Summary**
=====================

Here are the most important features of the `config.py` file:

* **Config File Loading**: The file reads a JSON configuration file named "config.json" from the same directory as the script.
* **Default Memory Location**: If the "memory_location" key in the config is empty or None, it defaults to "/tmp/autodoc-snapshots".
* **Memory Location Creation**: Before writing the config, the script creates the default memory location if it doesn't exist.
* **Config File Writing**: The file writes updates to the config file using the `json.dumps` method for pretty-printing.
* **Global Config Access**: The `read_config` function returns the loaded config dictionary, making it accessible globally.

## File Summary: agent.py
`agent.py`:

* Creates an OpenAI compliant LLM agent for autodocumentation purposes.
* Can be initialized with a configuration dictionary from `config.json`.
* Supports two LLM providers: Ollama and other (default).
* Provides methods to summarize files and directories using the LLM.
	+ `_summarize_file_system_prompt`: generates a prompt for summarizing file contents.
	+ `_summarize_directory_system_prompt`: generates a prompt for summarizing directory contents.
	+ `summarize_file`: uses the LLM to generate a summary of file contents.
	+ `summarize_directory`: uses the LLM to generate a summary of directory contents.

## File Summary: autodoc.py
Here is a summary of the `autodoc.py` file in markdown format:

*   **Autodoc Functionality**: The autodoc functionality generates auto README.md files for a provided repository (recursively).
*   **Command Line Interface**: The script has a command line interface that allows users to specify a repository, restore the README.md documents to their original state, or delete all the recursive README.md docs.
*   **Memory-Based Configuration**: The autodoc functionality uses memory-based configuration to store the summary of each directory/subdirectory in the repository.
*   **LLM Agent**: The script uses an LLM (Large Language Model) agent to summarize files and generate summaries for directories.
*   **Gitignore Handling**: The script handles gitignore files by ignoring files and directories that match the specified ignore regex.

## File Summary: main.py
`main.py` Summary
=================
### Overview

*   Runs the autodoc functionality from command line using `main.py`.

### Key Features

*   **Config Loading**: Loads configuration from `config.py` using the `read_config()` function.
*   **CLI Argument Parsing**: Parses command-line arguments using `autodoc.cli_setup()`.
*   **Autodoc Agent Creation**: Creates an instance of `AutodocLLMAgent` with the loaded configuration.
*   **Autodoc Operation**: Performs one of three autodoc operations based on the parsed CLI arguments:
    *   Restore: Restores documentation from a specified repository using `autodoc.restore_docs()`.
    *   Delete: Deletes documentation from a specified repository using `autodoc.delete_docs()`.
    *   Construct: Constructs documentation for an existing agent using `autodoc.construct_docs()`.

## File Summary: requirements.txt
**File Summary**

*   **`requirements.txt`**: A text file specifying the required dependencies for a project, including `langchain`, `langchain-ollama`, and `termcolor`. These libraries are necessary to run the software.

    This summary would be added to a README.md file.
