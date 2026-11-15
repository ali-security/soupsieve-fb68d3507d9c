"""Test attribute selectors."""
from .. import util
import signal
import threading
import time
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def assert_syntax_error_no_timeout(self, pattern, timeout=3):
        """
        Assert that compiling the pattern fails for syntax error, not timeout error.

        `SIGALRM` is used to abort a runaway compile where it is available (it is not
        on Windows, and it only works on the main thread); otherwise, we fall back to
        verifying the elapsed time.
        """

        use_alarm = hasattr(signal, 'SIGALRM') and threading.current_thread() is threading.main_thread()

        def timeout_handler(signum, frame):
            raise TimeoutError

        if use_alarm:
            previous = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

        passed = False
        start = time.monotonic()
        try:
            with self.assertRaises(sv.SelectorSyntaxError):
                sv.compile(pattern)
            passed = (time.monotonic() - start) < timeout
        except TimeoutError:
            pass
        finally:
            if use_alarm:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, previous if previous is not None else signal.SIG_DFL)
        self.assertTrue(passed)

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout('[a="' + ('x' * 300))

    def test_bad_attribute_unclosed_single_quote(self):
        """Test bad attribute with an unclosed single quoted value fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout("[a='" + ('x' * 300))

    def test_bad_contains_unclosed(self):
        """Test bad `:-soup-contains()` with an unclosed quoted value fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout(':-soup-contains("' + ('x' * 300))

    def test_bad_lang_unclosed(self):
        """Test bad `:lang()` with an unclosed quoted value fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout(":lang('" + ('x' * 300))
