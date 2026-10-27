from .lexer import Lexer
from .parser import Parser
from .semantic_analyzer import SemanticAnalyzer
from pprint import pprint
from .ast_formatter import format_ast
from .errors import display_error
from ._ansi import YELLOW, RESET
from ._cli_utils import stop_after, cli_err, compile_err
from .sb3_cgen import CodeGenerator
import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "file",
        help="src file to compile"
    )

    """--stop-after and --show-state are mainly for compiler development and testing"""
    parser.add_argument(
        "--stop-after",
        choices=["lexing", "parsing", "analysis"],
        help="stop compilation after the specified stage"
    )

    parser.add_argument(
        "--show-state",
        action="store_true",
        help="display the compiler state when compilation stops"
    )
    
    parser.add_argument(
        "--enable-uncompleted-codegen",
        action="store_true"
    )

    parser.add_argument(
        "-o", "--output",
        default="out.sb3",
        help="Output name for compiled file"
    )

    args = parser.parse_args()

    if args.show_state and not args.stop_after:
        parser.error("--show-state requires --stop-after")

    if args.output and not args.enable_uncompleted_codegen:
        parser.error("--output requires --enable_uncompleted_codegen")

    try:
        with open(args.file, "r") as f:
            src = f.read()
    except FileNotFoundError:
        cli_err(f"file not found: '{args.file}'")
        sys.exit(1)
    except PermissionError:
        cli_err(f"permission denied: '{args.file}'")
        sys.exit(1)
    except IsADirectoryError:
        cli_err(f"'{args.file}' is a directory, not a file")
        sys.exit(1)
    except OSError as e:
        cli_err(f"cannot read '{args.file}': {e.strerror}")
        
    lexer = Lexer(src)
    tokens, errors = lexer.lex()
    if errors: compile_err(errors, src)
    stop_after("lexing", tokens, args)
    
    parser = Parser(tokens)
    ast, errors = parser.parse()
    if errors: compile_err(errors, src)
    stop_after("parsing", format_ast(ast), args)
    
    analyzer = SemanticAnalyzer(ast)
    errors = analyzer.analyze()
    if errors: compile_err(errors, src)
    stop_after("analysis", format_ast(ast), args)

    if not args.enable_uncompleted_codegen:
        print(f"{YELLOW}note:{RESET} Codegen not added. Showing Abstract Syntax Tree instead.")
        print(format_ast(ast))
    else:
        cgen = CodeGenerator(ast)
        cgen.generate().package(args.output)
        
    return 0
