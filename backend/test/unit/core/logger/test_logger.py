import pytest
import logging
import queue
from unittest.mock import MagicMock, patch, call
from contextlib import contextmanager

from url_shortener.core.logger.logger import (
    Logger,
    FileUploadFilter,
    ContextAwareQueueHandler,
    initialize_logger,
    LOG_CONTEXT,
    add_context_to_log,
)


class TestFileUploadFilter:
    """Test the FileUploadFilter class."""

    def test_filter_file_data_redaction(self):
        """Test that file data is redacted from log messages."""
        filter_instance = FileUploadFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message with 'file_data': 'data:image/png;base64,ABC123'",
            args=(),
            exc_info=None
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "FILE DATA REDACTED" in record.msg

    def test_filter_image_url_redaction(self):
        """Test that image URLs are redacted from log messages."""
        filter_instance = FileUploadFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message with 'url': 'data:image/png;base64,ABC123'",
            args=(),
            exc_info=None
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "IMAGE DATA REDACTED" in record.msg

    def test_filter_no_redaction(self):
        """Test that normal messages pass through unchanged."""
        filter_instance = FileUploadFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="normal log message",
            args=(),
            exc_info=None
        )

        result = filter_instance.filter(record)

        assert result is True
        assert record.msg == "normal log message"


class TestContextAwareQueueHandler:
    """Test the ContextAwareQueueHandler class."""

    def test_prepare_adds_context(self):
        """Test that context is added to log records."""
        handler = ContextAwareQueueHandler(queue.Queue())
        LOG_CONTEXT.set({"user_id": "123", "request_id": "abc"})

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test",
            args=(),
            exc_info=None
        )

        prepared_record = handler.prepare(record)

        assert hasattr(prepared_record, "user_id")
        assert prepared_record.user_id == "123"
        assert hasattr(prepared_record, "request_id")
        assert prepared_record.request_id == "abc"


class TestLogger:
    """Test the Logger class."""

    def test_logger_initialization_colorful(self):
        """Test logger initialization with colorful output."""
        with patch('url_shortener.core.logger.logger.logging.handlers.QueueListener') as mock_listener_class:
            mock_listener = MagicMock()
            mock_listener_class.return_value = mock_listener

            logger = Logger(colorful_output=True)

            assert logger.colorful_output is True
            assert logger.queue_handler is not None
            mock_listener.start.assert_called_once()

    def test_logger_initialization_no_colorful(self):
        """Test logger initialization without colorful output."""
        with patch('url_shortener.core.logger.logger.logging.handlers.QueueListener') as mock_listener_class:
            mock_listener = MagicMock()
            mock_listener_class.return_value = mock_listener

            logger = Logger(colorful_output=False)

            assert logger.colorful_output is False
            mock_listener.start.assert_called_once()

    def test_logger_shutdown(self):
        """Test logger shutdown."""
        with patch('url_shortener.core.logger.logger.logging.handlers.QueueListener') as mock_listener_class:
            mock_listener = MagicMock()
            mock_listener_class.return_value = mock_listener

            logger = Logger()
            logger.shutdown()

            mock_listener.stop.assert_called_once()


class TestAddContextToLog:
    """Test the add_context_to_log context manager."""

    def test_add_context_to_log(self):
        """Test adding context to logs."""
        LOG_CONTEXT.set({})

        with add_context_to_log(user_id="123"):
            context = LOG_CONTEXT.get()
            assert context["user_id"] == "123"

        # Context should be reset after exit
        context = LOG_CONTEXT.get()
        assert context == {}

    def test_add_context_to_log_nested(self):
        """Test nested context."""
        LOG_CONTEXT.set({"outer": "value"})

        with add_context_to_log(inner="value2"):
            context = LOG_CONTEXT.get()
            assert context["outer"] == "value"
            assert context["inner"] == "value2"

        # Outer context should remain
        context = LOG_CONTEXT.get()
        assert context == {"outer": "value"}


class TestInitializeLogger:
    """Test the initialize_logger function."""

    @patch('url_shortener.core.logger.logger.Logger')
    def test_initialize_logger(self, mock_logger_class):
        """Test logger initialization."""
        mock_logger_instance = MagicMock()
        mock_logger_class.return_value = mock_logger_instance

        result = initialize_logger()

        assert result == mock_logger_instance
        mock_logger_class.assert_called_once()
