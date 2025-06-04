import autodoc
from agent import AutodocLLMAgent
from config import read_config

if __name__ == "__main__":
    """ Runs the autodoc functionality from command line """
    
    config = read_config()
    cli_args = autodoc.cli_setup()
    autodoc_agent = AutodocLLMAgent(config)

    if cli_args.restore: 
        autodoc.restore_docs(cli_args.repo)
    elif cli_args.delete:
        autodoc.delete_docs(cli_args.repo)
    else:
        autodoc.construct_docs(autodoc_agent, cli_args.repo)
