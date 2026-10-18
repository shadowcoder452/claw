from claw.lexer import Lexer
from claw.parser import Parser
from claw.semantic_analyzer import SemanticAnalyzer


def analyze(source: str):
    tokens, lexer_errors = Lexer(source).lex()
    assert not lexer_errors

    statements, parser_errors = Parser(tokens).parse()
    assert not parser_errors

    analyzer = SemanticAnalyzer(statements)
    errors = analyzer.analyze()
    return analyzer, errors


def error_causes(errors):
    return [error.cause for error in errors]


def test_declared_variable_can_be_referenced_and_assigned():
    _, errors = analyze("""
        var count
        fn main() {
            count = 1
            count
        }
    """)

    assert errors == []


def test_undefined_identifier_is_reported():
    _, errors = analyze("fn main() { missing }")

    assert error_causes(errors) == ["undefined object `missing` referenced"]


def test_assignment_to_undefined_identifier_is_reported():
    _, errors = analyze("fn main() { missing = 1 }")

    assert error_causes(errors) == ["assigned to undefined object `missing`"]


def test_redeclaring_variable_is_reported():
    _, errors = analyze("var item var item")

    assert error_causes(errors) == ["object `item` redefined"]


def test_duplicate_parameters_are_reported():
    _, errors = analyze("fn main(value, value) {}")

    assert error_causes(errors) == ["duplicate parameter"]


def test_function_can_be_called_with_the_correct_number_of_arguments():
    _, errors = analyze("""
        fn identity(value) { value }
        fn main() { identity(1) }
    """)

    assert errors == []


def test_calling_undefined_function_is_reported():
    _, errors = analyze("fn main() { missing() }")

    assert error_causes(errors) == ["undefined object `missing` referenced"]


def test_calling_variable_is_reported():
    _, errors = analyze("var item fn main() { item() }")

    assert error_causes(errors) == ["called object `item` is not a function"]


def test_wrong_argument_count_is_reported():
    _, errors = analyze("""
        fn add(left, right) { left }
        fn main() { add(1) }
    """)

    assert error_causes(errors) == ["expected 2 arguments but got 1"]


def test_assigning_to_function_is_reported():
    _, errors = analyze("fn work() {} fn main() { work = 1 }")

    assert error_causes(errors) == ["variable required as target of assignment"]


def test_redeclaring_function_is_reported():
    _, errors = analyze("fn work() {} fn work() {}")

    assert error_causes(errors) == ["cannot redeclare function work"]


def test_analysis_continues_after_an_error():
    _, errors = analyze("fn main() { first_missing second_missing }")

    assert error_causes(errors) == [
        "undefined object `first_missing` referenced",
        "undefined object `second_missing` referenced",
    ]


def test_function_parameters_are_scoped_to_the_function():
    _, errors = analyze("""
        fn first(value) { value }
        fn second() { value }
    """)

    assert error_causes(errors) == ["undefined object `value` referenced"]
