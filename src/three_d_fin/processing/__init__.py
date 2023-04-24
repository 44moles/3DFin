import argparse
import configparser
import os
from pathlib import Path

import laspy

from three_d_fin import __about__
from three_d_fin.gui.layout import Application
from three_d_fin.processing import algorithm, configuration


def launch_application() -> int:
    """Parse the command line and launch the GUI or the CLI application.

    Main entry point for the 3DFin application:
        - Launch the GUI if the command is called without aguments.

        - Launch the CLI by appending the 'cli' subcommand to the command. For other
          arguments, the reader should return to the body of the function.

    Returns
    -------
    exit_code : int
        POSIX minimal exit code (0 = SUCCESS, 1 = ERROR)
    """
    EXIT_ERROR = 1
    EXIT_SUCCESS = 0

    parser = argparse.ArgumentParser(
        prog="3DFin",
        description=f"""
            {__about__.__copyright_info_1__}
            {__about__.__copyright_info_2__}
            {__about__.__license_msg__}""",
    )
    parser.add_argument(
        "--version", "-v", action="version", version=__about__.__version__
    )

    # Create a subparser for cli subcommand
    subparsers = parser.add_subparsers(dest="subcommand")
    cli_subparser = subparsers.add_parser(
        "cli", help="launch the app in command line mode"
    )
    cli_subparser.add_argument("input_file", help="Las or Laz input file")
    cli_subparser.add_argument(
        "output_directory", help="output directory where to put the results"
    )
    cli_subparser.add_argument("params_file", help=".ini files with parameters")
    cli_subparser.add_argument(
        "--export_txt",
        action="store_true",
        help="Export tabular data in ASCII CSV files instead of XLSX",
    )
    cli_subparser.add_argument(
        "--normalize", action="store_true", help="Normalize the data with CSF algorithm"
    )
    cli_subparser.add_argument(
        "--denoise",
        action="store_true",
        help="Denoise the data, if outliers below ground level are expected",
    )
    cli_subparser.add_argument(
        "--version", "-v", action="version", version=__about__.__version__
    )

    cli_parse = parser.parse_args()

    print(__about__.__copyright_info_1__)
    print(__about__.__copyright_info_2__)
    print(__about__.__license_msg__)
    # No subcommand, launch GUI
    if cli_parse.subcommand is None:
        fin_app = Application(algorithm.fin_callback)
        _ = fin_app.run()
        # TODO it's always sucess for now but we should do exception handling
        return EXIT_SUCCESS

    # Else, the CLI case
    # First, read the param file and sanitize the input
    config_path = Path(cli_parse.params_file)
    if not config_path.exists() or not config_path.is_file():
        print("Parameters: File does not exist")
        return EXIT_ERROR

    with config_path.open("r") as f:
        params = configparser.ConfigParser()
        try:
            params.read_file(f)
        except configparser.ParsingError:
            print("Parameters: invalid .ini file")
            return EXIT_ERROR

    try:
        # TODO: We should have a validation class here
        valid_params = configuration._validate_config(params)
    except configparser.NoOptionError as error:
        print(
            f"Parameters: invalid option '{error.option}' in section '{error.section}'"
        )
        return EXIT_ERROR
    except ValueError as error:
        print(f"Parameters: {error.args[0]}")
        return EXIT_ERROR

    # Second, We check las file validity
    input_las = Path(cli_parse.input_file)
    if not input_las.exists() or not input_las.is_file():
        print("Input file: file does not exists")
        return EXIT_ERROR
    try:
        laspy.open(input_las, read_evlrs=False)
    except laspy.LaspyException:
        print("Input file: invalid las file")
        return EXIT_ERROR

    # At last, We check the validity of the current output directory
    output_dir = Path(cli_parse.output_directory)
    if (
        not output_dir.exists()
        or not output_dir.is_dir()
        or not os.access(
            output_dir, os.W_OK
        )  # os.access won't work very well on Windows, we may still have to mess with exceptions
    ):
        print("Invalid output directory")
        return EXIT_ERROR

    # Wrap all in the misc section
    valid_params["misc"]["is_normalized"] = not cli_parse.normalize
    valid_params["misc"]["is_noisy"] = cli_parse.denoise
    valid_params["misc"]["txt"] = cli_parse.export_txt
    valid_params["misc"]["input_las"] = cli_parse.input_file
    valid_params["misc"]["output_dir"] = cli_parse.output_directory

    # Run processing
    algorithm.fin_callback(valid_params)
    # TODO it's always sucess for now but we should do exception handling
    return EXIT_SUCCESS