import shutil

import pytest
from six import PY2

from pre_commit_hooks.pretty_format_json import main
from pre_commit_hooks.pretty_format_json import parse_num_to_int
from testing.util import get_resource_path


def test_parse_num_to_int():
    assert parse_num_to_int('0') == 0
    assert parse_num_to_int('2') == 2
    assert parse_num_to_int('\t') == '\t'
    assert parse_num_to_int('  ') == '  '


@pytest.mark.parametrize(
    ('filename', 'expected_retval'), (
        ('not_pretty_formatted_json.json', 1),
        ('unsorted_pretty_formatted_json.json', 1),
        ('non_ascii_pretty_formatted_json.json', 1),
        ('pretty_formatted_json.json', 0),
    ),
)
def test_main(filename, expected_retval):
    ret = main([get_resource_path(filename)])
    assert ret == expected_retval


@pytest.mark.parametrize(
    ('filename', 'expected_retval'), (
        ('not_pretty_formatted_json.json', 1),
        ('unsorted_pretty_formatted_json.json', 0),
        ('non_ascii_pretty_formatted_json.json', 1),
        ('pretty_formatted_json.json', 0),
    ),
)
def test_unsorted_main(filename, expected_retval):
    ret = main(['--no-sort-keys', get_resource_path(filename)])
    assert ret == expected_retval


@pytest.mark.skipif(PY2, reason='Requires Python3')
@pytest.mark.parametrize(
    ('filename', 'expected_retval'), (
        ('not_pretty_formatted_json.json', 1),
        ('unsorted_pretty_formatted_json.json', 1),
        ('non_ascii_pretty_formatted_json.json', 1),
        ('pretty_formatted_json.json', 1),
        ('tab_pretty_formatted_json.json', 0),
    ),
)
def test_tab_main(filename, expected_retval):  # pragma: no cover
    ret = main(['--indent', '\t', get_resource_path(filename)])
    assert ret == expected_retval


def test_non_ascii_main():
    ret = main((
        '--no-ensure-ascii',
        get_resource_path('non_ascii_pretty_formatted_json.json'),
    ))
    assert ret == 0


def test_autofix_main(tmpdir):
    srcfile = tmpdir.join('to_be_json_formatted.json')
    shutil.copyfile(
        get_resource_path('not_pretty_formatted_json.json'),
        srcfile.strpath,
    )

    # now launch the autofix on that file
    ret = main(['--autofix', srcfile.strpath])
    # it should have formatted it
    assert ret == 1

    # file was formatted (shouldn't trigger linter again)
    ret = main([srcfile.strpath])
    assert ret == 0


def test_orderfile_get_pretty_format():
    ret = main((
        '--top-keys=alist', get_resource_path('pretty_formatted_json.json'),
    ))
    assert ret == 0


def test_not_orderfile_get_pretty_format():
    ret = main((
        '--top-keys=blah', get_resource_path('pretty_formatted_json.json'),
    ))
    assert ret == 1


def test_top_sorted_get_pretty_format():
    ret = main((
        '--top-keys=01-alist,alist', get_resource_path('top_sorted_json.json'),
    ))
    assert ret == 0


def test_badfile_main():
    ret = main([get_resource_path('ok_yaml.yaml')])
    assert ret == 1
