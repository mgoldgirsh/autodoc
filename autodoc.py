from ollama import chat 
from ollama import ChatResponse
import os
import re


def file_system_prompt() -> str: 
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


def dir_system_prompt() -> str: 
    return """
    You are a professional software engineer. You can quickly understand code files and other files that are required to build software.
    You are given a README.md file for a specified directory

    Your goal is to generate a ONE SENTENCE description of the directory readme file, that captures the essence of all the files in the directory.
    The generated sentence should be in plaintext and capturing the essence of the directory. 

    """.strip()


def ignore_files_regex() -> str: 
    ignore_paths = [r'vendor', r'.git', r'results', r'.ansible', r'.gitignore', r'.venv', r"README.md", r'.pdf', r'go.mod', r'go.sum']
    return '?(' + "|".join(ignore_paths) + ')'


def read_file(filepath: str) -> str: 
    with open(filepath, 'r') as f: 
        return f"`{filepath}`:\n```\n" + f.read() + "\n```"


def llm_file_analysis(file_contents: str) -> str: 
    response: ChatResponse = chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': file_system_prompt() 
        },
        {
            'role': 'user',
            'content': file_contents
        },
    ], options={"num_ctx": 16384})
    return response.message.content


def llm_dir_analysis(dir_readme: str) -> str:
    response: ChatResponse = chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': dir_system_prompt() 
        },
        {
            'role': 'user',
            'content': dir_readme
        },
    ], options={"num_ctx": 16384})
    return response.message.content


def write_directory_summary(readme_file: str, dir_path: str, dir_sumamry: str) -> None: 
    with open(readme_file, 'a') as f:
        f.write(f"\n## Summary: {dir_path}\n")
        f.write(dir_sumamry + "\n")
    return None


def construct_docs(repo: str) -> dict:
    """ Given a repo at certain string, construct readme docs for every folder + subfolder in the repo"""

    ignore_regex = os.path.join(repo, "(.*)" , ignore_files_regex())

    seen: dict[str, str] = {}  # the directory seen and the summary associated with it 

    for path, folders, files in os.walk(repo, topdown=False): 
        short_path = path[len(repo):] if path[len(repo):] != "" else os.path.basename(repo)

        if re.match(ignore_regex, path):
            continue
        else:
            print(f"Started summary of: `{short_path}`")
            
        if os.path.isdir(path):
            readme_file = os.path.join(path, "README.md")
        else:
            readme_file = os.path.join(os.path.dirname(path), "README.md")
        
        for folder in folders:
            folderpath = os.path.join(short_path, folder)
            if folderpath in seen: 
                write_directory_summary(readme_file, folderpath, seen[folderpath])
                print(f"  Summarizing Seen Directory: `{folderpath}`")

        
        if len(files) == 0:
            continue 

        with open(readme_file, 'a') as f:

            f.write(f"\n## Summary: {short_path}\n")

            try: 
                for filename in files: 
                    filepath = os.path.join(path, filename)
                    short_filepath = filepath[len(repo):]

                    # dont read bad files
                    if re.match(ignore_regex, filepath):
                        continue

                    # 1. read file
                    try: 
                        file_contents = read_file(filepath)
                        print(f"  Summarizing File: `{short_filepath}`")
                    except UnicodeDecodeError as e: 
                        print(f"  Failed Summarizing File: `{short_filepath}`")
                        continue

                    # 2. analyze file with llm 
                    summarization = f"\n### File: {short_filepath}\n " + llm_file_analysis(file_contents) + "\n"

                    # 3. write analysis into readme
                    f.write(summarization)
                    f.flush()
            finally:
                f.flush()
                f.close()

        
        # now add this to the directory summarization
        with open(readme_file, 'r') as f:
            dir_contents = f.read()
        seen[short_path] = llm_dir_analysis(dir_contents)


    print(f"\nCompleted autodoc: `{os.path.basename(repo)}`")
    return seen


if __name__ == "__main__":
    construct_docs("<path_here>")
