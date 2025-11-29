import pytest
import json
import logging
from unittest.mock import patch

from url_shortener.core.logger.colorfulFormatter import ColoredJSONFormatter, Colors


class TestColors:
    """Test the Colors class."""

    def test_colors_attributes(self):
        """Test that color constants are defined."""
        assert Colors.RESET == "\033[0m"
        assert Colors.RED == "\033[31m"
        assert Colors.GREEN == "\033[32m"
        assert Colors.YELLOW == "\033[33m"
        assert Colors.BLUE == "\033[34m"
        assert Colors.BOLD == "\033[1m"


class TestColoredJSONFormatter:
    """Test the ColoredJSONFormatter class."""

    @pytest.fixture
    def formatter(self):
        """Create a formatter instance."""
        return ColoredJSONFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            rename_fields={"levelname": "level", "asctime": "time"}
        )

    @pytest.fixture
    def log_record(self):
        """Create a sample log record."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        return record

    @patch('url_shortener.core.logger.colorfulFormatter.jsonlogger.JsonFormatter.format')
    def test_format_info_level(self, mock_super_format, formatter, log_record):
        """Test formatting an INFO level log."""
        mock_super_format.return_value = json.dumps({
            "time": "2023-01-01 12:00:00",
            "name": "test_logger",
            "level": "INFO",
            "message": "Test message"
        })

        result = formatter.format(log_record)

        assert "INFO" in result
        assert "ℹ️" in result  # INFO emoji
        assert "Test message" in result
        assert Colors.CYAN in result  # Logger name color

    @patch('url_shortener.core.logger.colorfulFormatter.jsonlogger.JsonFormatter.format')
    def test_format_error_level(self, mock_super_format, formatter):
        """Test formatting an ERROR level log."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error message",
            args=(),
            exc_info=None
        )

        mock_super_format.return_value = json.dumps({
            "time": "2023-01-01 12:00:00",
            "name": "test_logger",
            "level": "ERROR",
            "message": "Error message"
        })

        result = formatter.format(record)

        assert "ERROR" in result
        assert "❌" in result  # ERROR emoji
        assert Colors.BRIGHT_RED in result  # ERROR color

    @patch('url_shortener.core.logger.colorfulFormatter.jsonlogger.JsonFormatter.format')
    def test_format_with_context_fields(self, mock_super_format, formatter, log_record):
        """Test formatting with additional context fields."""
        mock_super_format.return_value = json.dumps({
            "time": "2023-01-01 12:00:00",
            "name": "test_logger",
            "level": "INFO",
            "message": "Test message",
            "user_id": "123",
            "request_id": "abc"
        })

        result = formatter.format(log_record)

        assert "user_id" in result
        assert "request_id" in result
        assert "123" in result
        assert "abc" in result

    @patch('url_shortener.core.logger.colorfulFormatter.jsonlogger.JsonFormatter.format')
    def test_format_debug_level(self, mock_super_format, formatter):
        """Test formatting a DEBUG level log."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="Debug message",
            args=(),
            exc_info=None
        )

        mock_super_format.return_value = json.dumps({
            "time": "2023-01-01 12:00:00",
            "name": "test_logger",
            "level": "DEBUG",
            "message": "Debug message"
        })

        result = formatter.format(record)

        assert "DEBUG" in result
        assert "🐞" in result  # DEBUG emoji

    @patch('url_shortener.core.logger.colorfulFormatter.jsonlogger.JsonFormatter.format')
    def test_format_warning_level(self, mock_super_format, formatter):
        """Test formatting a WARNING level log."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Warning message",
            args=(),
            exc_info=None
        )

        mock_super_format.return_value = json.dumps({
            "time": "2023-01-01 12:00:00",
            "name": "test_logger",
            "level": "WARNING",
            "message": "Warning message"
        })

        result = formatter.format(record)

        assert "WARNING" in result
        assert "⚠️" in result  # WARNING emoji

    @patch('url_shortener.core.logger.colorfulFormatter.jsonlogger.JsonFormatter.format')
    def test_format_critical_level(self, mock_super_format, formatter):
        """Test formatting a CRITICAL level log."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.CRITICAL,
            pathname="test.py",
            lineno=1,
            msg="Critical message",
            args=(),
            exc_info=None
        )

        mock_super_format.return_value = json.dumps({
            "time": "2023-01-01 12:00:00",
            "name": "test_logger",
            "level": "CRITICAL",
            "message": "Critical message"
        })

        result = formatter.format(record)

        assert "CRITICAL" in result
        assert "🔥" in result  # CRITICAL emoji
