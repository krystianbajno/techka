
def print_full_help(argparse, parser, subparsers):
    """Prints help for ALL commands and subcommands."""
    print("\nMain Command Help:\n")
    parser.print_help()
    print("\nSubcommand Help:\n")

    for subcommand_name, subparser in subparsers.choices.items():
        print(f"\nHelp for '{subcommand_name}' command:")
        subparser.print_help()

        for sub_action in subparser._actions:
            if isinstance(sub_action, argparse._SubParsersAction):
                for nested_name, nested_subparser in sub_action.choices.items():
                    print(f"\nHelp for '{subcommand_name} {nested_name}' subcommand:")
                    nested_subparser.print_help()
