from termcolor import colored 
from typing import Any, Dict, Optional, List, Tuple
import argparse
import sys
import os
import re
import io

from config import read_config
from agent import AutodocLLMAgent


# ----- Utility Functions -----
def generate_ignored_paths(repo: str, additional_ignores: list[str] = None) -> str:
    """Generate the ignored path regex.

    Args:
        repo (str): the base repo you are ignoring files in
        additional_ignores (list[str], optional): A list of additional files + directories that you want to ignore. Defaults to None.

    Returns:
        str: a regex string that will contain all the ignored paths you don't want to look at when generating autodoc
    """
    ignore_paths = read_config()['ignore_paths']
    
    if additional_ignores:
        ignore_paths += additional_ignores
    
    ignore_paths_re = '?(' + "|".join(set(ignore_paths)) + ')'
    full_ignore_paths = os.path.join(repo, "(.*)" , ignore_paths_re)
    return full_ignore_paths


def read_gitignore(path: str) -> list[str]:
    """Reads the gitignore file located at the provided path

    Args:
        path (str): the path to read the gitignore file at

    Returns:
        list[str]: a list of all the .gitignore files you want to have ignored 
    """
    if os.path.exists(path):
        with open(path, 'r') as f: 
            return f.read().strip().split("\n")
    else:
        return []


def read_file(repo: str, short_filepath: str) -> Optional[str]:
    """Tries to read a file a file and specified filepath and return its formatted contents. 
       NOTE: this function assumes the file exists 

    Args:
        repo (str): the repo to read the file from
        short_filepath (str): the shortened filepath to read the file from (without repo prefix)

    Returns:
        Optional[str]: the string contents of the file formatted in a nice way. Otherwise the none if the file type can not be decoded.
    """
    try: 
        with open(os.path.join(repo, short_filepath), 'r') as f: 
            print(f"  Summarizing File: `{short_filepath}`")
            return f"`{short_filepath}`:\n```\n" + f.read() + "\n```"
    except UnicodeDecodeError as e:
        print(f"  Failed Summarizing File: `{short_filepath}` | " + str(e))


def write_summary(f: io.TextIOWrapper, path: str, summary: str) -> str:
    """Writes a summary from a specified path to an open buffer.

    Args:
        f (io.TextIOWrapper): the open buffer to write to
        path (str): the location where you summarized from
        summary (str): the summary of the location specified in the path

    Returns: 
        str: the string that was written to the open buffer
    """
    prefix = "Directory" if os.path.isdir(path) else "File"
    f.write(f"\n## {prefix} Summary: {path}\n{summary}\n")
    f.flush()
    return f"\n## {prefix} Summary: {path}\n{summary}\n"


def take_snapshot(repo: str) -> None:
    """Takes a snapshot of the repositories README current document configuration, and saves it in the location 
       specified by the config.

    Args:
        repo (str): the repository to take a snapshot of
    """
    memory_directory = read_config()['memory_location']
    memory_file = os.path.join(memory_directory, os.path.basename(repo) + ".txt")
    saved = set()
    with open(memory_file, 'w') as memory:
        for path, _, _ in os.walk(repo, topdown=False): 

            # find/create the readme file in each directory 
            if os.path.isdir(path):
                readme_file = os.path.join(path, "README.md")
            else:
                readme_file = os.path.join(os.path.dirname(path), "README.md")
            
            gitignore_contents = read_gitignore(os.path.join(path, ".gitignore"))
            ignore_regex = generate_ignored_paths(repo, gitignore_contents)
            if re.match(ignore_regex, path):
                continue

            if readme_file not in saved:
                if os.path.exists(readme_file):
                    with open(readme_file, 'r') as f: 
                        memory.write(f'{readme_file},{f.read()}')
                else:
                    memory.write(f'{readme_file},')
                memory.flush()
                saved.add(readme_file)


def read_snapshot(snapshot_loc: str) -> List[Tuple[str, str]]:
    """Reads the snapshot and returns the list of [filepath, contents] that needs to be rewrote 

    Args:
        snapshot_loc (str): the snapshot location to read from

    Returns:
        List[Tuple[str, str]]: a list of [filepath, contents] that describes the document configuration
    """
    with open(snapshot_loc, 'r') as f:
        snapshot = f.readlines()
    
    snapshot_formatted = [line.strip().split(',') for line in snapshot]
    return snapshot_formatted


# ----- Main Functions -----
def construct_docs(llm: AutodocLLMAgent, repo: str) -> Dict[str, str]:
    """Given a autodoc llm agent and repository to autodoc, generate README documents for every directory in the repository provided. 
       If a README document already exists append to it.

    Args:
        llm (AutodocLLMAgent): the llm agent used to generate the autodoc fuctionaltiy
        repo (str): the repository you want to generate autodocs for

    Returns:
        Dict[str, str]: a dictionary of all the directories/subdirectories in the repository and a one sentence summary of each of them.
    """
    take_snapshot(repo)   # takes a snapshot of the current README document configuration
    seen: dict[str, str] = {}  # the directory seen and the summary associated with it 
    for path, folders, files in os.walk(repo, topdown=False): 
        # generate a short path for the dir we are in
        short_path = path[len(repo):] if path[len(repo):] != "" else os.path.basename(repo)

        # find/create the readme file in each directory 
        if os.path.isdir(path):
            readme_file = os.path.join(path, "README.md")
            gitignore_contents = read_gitignore(os.path.join(path, ".gitignore"))
        else:
            readme_file = os.path.join(os.path.dirname(path), "README.md")
            gitignore_contents = read_gitignore(os.path.join(os.path.dirname(path), ".gitignore"))

        # update the ignore regex using the repo's exisiting .gitignore file
        ignore_regex = generate_ignored_paths(repo, gitignore_contents)

        # if the file we are in is ignored then continue, otherwise start summarization
        if re.match(ignore_regex, path):
            continue
        else:
            print(colored(f"Started summary of: `{short_path}`", "light_blue"))
            
        # filter all the files we plan to look at by the ignore regex
        filtered_files = list(filter(lambda filename: False if re.match(ignore_regex, os.path.join(path, filename)) else True, files))
        
        # Write the README.md file in append + read mode for every file
        overall_summary = ""
        with open(readme_file, 'a') as f:
            f.write(f"\n# Overall Summary: {short_path}\n")

            # Look at the folders in the path and if we already seen the folder add it's summary to the readme document.
            for folder in folders:
                folderpath = os.path.join(short_path, folder)
                if folderpath in seen:  # INVARIANT: we are not looking at ignored folders
                    overall_summary += write_summary(f, folderpath, seen[folderpath])
                    print(f"  Summarizing Seen Directory: `{folderpath}`")

            # Look at the files in the path and add its summary (if not ignored) to the readme document.
            for short_filepath in filtered_files: 
                # 1. read file if possible
                file_contents = read_file(repo, short_filepath)

                # 2. use the llm to summarize the file and write the summary
                overall_summary += write_summary(f, short_filepath, llm.summarize_file(file_contents))


        # Now when all the files in the directory have been read summarize the directory and add it to seen directories
        seen[short_path] = llm.summarize_directory(overall_summary)


    print(colored(f"\nCompleted autodoc: `{os.path.basename(repo)}`", "light_green"))
    return seen


def restore_docs(repo: str) -> None:
    """Reverts README document configuration for a repository based off the autodocs memory.

    Args:
        repo (str): the repository to restore the README documents for.
    """
    memory_directory = read_config()['memory_location']
    memory_file = os.path.join(memory_directory, os.path.basename(repo) + ".txt")

    if not os.path.exists(memory_file):
        print(colored(f"\nRestore operation could not be completed no memory file: `{memory_file}`", "light_red"))
        return

    memory_list = read_snapshot(memory_file)
    for readme_path, readme_contents in memory_list:
        if not os.path.exists(readme_path):
            continue

        if readme_contents != "":
            with open(readme_path, 'w') as f: 
                f.write(readme_contents)
        else:
            os.remove(readme_path)

    print(colored(f"\Restored original README: `{os.path.basename(repo)}`", "light_green"))


def delete_docs(repo: str) -> None:
    """Deletes all the README files associated with every directory/subdirectory of the repository.

    Args:
        repo (str): the repository to delete all the recursive readme files at.
    """
    deleted = set()
    for path, _, _ in os.walk(repo, topdown=False): 


        # find/create the readme file in each directory 
        if os.path.isdir(path):
            readme_file = os.path.join(path, "README.md")
        else:
            readme_file = os.path.join(os.path.dirname(path), "README.md")

        gitignore_contents = read_gitignore(os.path.join(path, ".gitignore"))
        ignore_regex = generate_ignored_paths(repo, gitignore_contents)
        if re.match(ignore_regex, path):
            continue

        if readme_file not in deleted:
            os.remove(readme_file)
            deleted.add(readme_file)

    print(colored(f"\nDeleted autodoc README: `{os.path.basename(repo)}`", "light_green"))


# ----- Setup Command Line Interface -----
def cli_setup() -> Any:
    """Setup the command line argument parser to use with command line

    Returns:
        Any: all the commandline arguments that the user included
    """
    
    # enable colors on windows machines
    if sys.platform.startswith('win'):
        os.system('color')

    parser = argparse.ArgumentParser(description='The comand line interface for autodoc a process which generates auto README.md files for a provided repository (recursively)')
    parser.add_argument("repo", help='the repository you want to autodoc', type=str, nargs="?", default=os.getcwd())
    parser.add_argument("-s", "--restore", help='restore the README.md in a specified repository to their original state (before running autodoc)', action='store_true')
    parser.add_argument("-d", "--delete", help='delete all the README.md docs at a specified repository (recursively)', action='store_true')

    return parser.parse_args()
