import json
from logging import INFO, LogRecord
from unittest.mock import MagicMock, patch

from aws_lambda_powertools import Logger

from common.logging.logger import CustomFormatter, setup_logger


def test_custom_formatter_extract_log_exception_list_with_exception():
    exc_info = (Exception, Exception("test exception"), MagicMock())
    log_record = LogRecord(
        name="test", level=10, pathname="test", lineno=10, msg="Test message", args=(), exc_info=exc_info
    )

    formatter = CustomFormatter()

    with patch.object(formatter, "formatException", return_value="Traceback line 1\nTraceback line 2"):
        trace, exc_name = formatter._extract_log_exception_list(log_record)

    assert trace == ["Traceback line 1", "Traceback line 2"]
    assert exc_name == "Exception"


def test_custom_formatter_extract_log_exception_without_exception():
    log_record = LogRecord(
        name="test", level=10, pathname="test", lineno=10, msg="Test message", args=(), exc_info=None
    )

    formatter = CustomFormatter()

    trace, exc_name = formatter._extract_log_exception_list(log_record)

    assert trace is None
    assert exc_name is None


def test_format_includes_exception_list():
    try:
        raise Exception("test exception")
    except Exception as e:
        exc_info = (type(e), e, e.__traceback__)
    log_record = LogRecord(
        name="test_logger",
        level=10,
        pathname="test_path",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=exc_info,
    )
    formatter = CustomFormatter()

    # Call format and deserialize the result to check the structure
    formatted_log = formatter.format(log_record)
    formatted_log_dict = json.loads(formatted_log)

    # Expected exception traceback split into lines
    expected_exception_list = formatter.formatException(log_record.exc_info).splitlines()

    # Assertions: check that the exception in the log is a list
    assert formatted_log_dict["exception"] == expected_exception_list
    assert formatted_log_dict["exception_name"] == exc_info[0].__name__


def test_setup_logger():
    service_name = "test_service"
    log_level = INFO

    logger = setup_logger(service=service_name, level=log_level)

    assert isinstance(logger, Logger)
    assert logger.service == service_name
    assert logger.level == log_level
    assert isinstance(logger.logger_formatter, CustomFormatter)
