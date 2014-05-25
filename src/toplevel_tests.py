import os
import unittest
from tempfile import NamedTemporaryFile

from main import entry_point, USAGE
from test_utils import mock_stdout


class TopLevelWithoutArgsTest(unittest.TestCase):
    def test_no_args_return_value(self):
        return_value = entry_point([])
        self.assertNotEqual(return_value, 0)
        
    def test_no_args_prints_usage(self):
        with mock_stdout() as stdout:
            entry_point([])

        self.assertEqual(stdout.getvalue(), USAGE + '\n')


class TopLevelSnippetTest(unittest.TestCase):
    def test_snippet(self):
        with mock_stdout() as stdout:
            entry_point(['trifle', '-i', '(+ 1 2)'])

        self.assertEqual(stdout.getvalue(), '3\n')

    def test_snippet_error(self):
        """If given a snippet that throws an error, we should have a non-zero
        return code.

        """
        return_value = entry_point(['trifle', '-i', '(+ 1 i-dont-exist)'])
        self.assertNotEqual(return_value, 0)

    def test_snippet_error_as_value(self):
        """If given a snippet that returns an error, we should have a return
        code of zero.

        """
        return_value = entry_point([
            'trifle', '-i',
            '(try (/ 1 0) :catch error e e)'
        ])
        self.assertEqual(return_value, 0)

    def test_snippet_evaluate_empty_list_catch(self):
        # Regression test.
        return_value = entry_point([
            'trifle', '-i',
            '(try () :catch error e 1)'
        ])
        self.assertEqual(return_value, 0)

    def test_snippet_lex_error(self):
        """If given a snippet that throws an error during lexing, we should
        have a non-zero return code.

        """
        return_value = entry_point(['trifle', '-i', '1/0'])
        self.assertNotEqual(return_value, 0)


class TopLevelFileTest(unittest.TestCase):
    def test_eval_file(self):
        with NamedTemporaryFile() as f:
            f.write('(set! f (open "foo.txt" :write)) (close! f)')
            f.flush()

            entry_point(['trifle', f.name])

        self.assertTrue(os.path.exists("foo.txt"))

        os.remove("foo.txt")

    def test_eval_file_error(self):
        with NamedTemporaryFile() as f:
            f.write('(div 1 0)')
            f.flush()
                
            return_value = entry_point(['trifle', f.name])

        self.assertNotEqual(return_value, 0)

    def test_eval_file_lex_error(self):
        with NamedTemporaryFile() as f:
            f.write('1/0')
            f.flush()
                
            return_value = entry_point(['trifle', f.name])

        self.assertNotEqual(return_value, 0)
