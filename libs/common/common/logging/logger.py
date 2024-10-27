from logging import LogRecord

from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatters.datadog import DatadogLogFormatter


class CustomFormatter(DatadogLogFormatter):
    def format(self, record: LogRecord) -> str:
        """Format logging record as structured JSON str"""
        formatted_log = self._extract_log_keys(log_record=record)
        formatted_log["message"] = self._extract_log_message(log_record=record)

        # exception and exception_name fields can be added as extra key
        # in any log level, we try to extract and use them first
        extracted_exception, extracted_exception_name = self._extract_log_exception_list(log_record=record)
        formatted_log["exception"] = formatted_log.get("exception", extracted_exception)
        formatted_log["exception_name"] = formatted_log.get("exception_name", extracted_exception_name)
        if self.serialize_stacktrace:
            # Generate the traceback from the traceback library
            formatted_log["stack_trace"] = self._serialize_stacktrace(log_record=record)
        formatted_log["xray_trace_id"] = self._get_latest_trace_id()
        formatted_log = self._strip_none_records(records=formatted_log)

        return self.serialize(log=formatted_log)

    def _extract_log_exception_list(self, log_record: LogRecord) -> tuple[list, str] | tuple[None, None]:
        if log_record.exc_info:
            # Split traceback by newline characters
            return self.formatException(log_record.exc_info).splitlines(), log_record.exc_info[0].__name__  # type: ignore

        return None, None


def setup_logger(
    service: str | None = None,
    level: str | int | None = None,
    **kwargs,
) -> Logger:
    logger = Logger(
        service=service,
        level=level,
        logger_formatter=CustomFormatter(),
        **kwargs,
    )
    return logger
