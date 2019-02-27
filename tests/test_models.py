# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import pytest

from pytest_testdox import formatters
from pytest_testdox.models import Node, PatternConfig, Result


@pytest.fixture
def node():
    return Node(title='title', class_name='class_name', module_name='module')


@pytest.fixture
def report():
    return mock.Mock(
        nodeid='folder/test_file.py::test_title',
        outcome='passed'
    )


@pytest.fixture
def pattern_config():
    return PatternConfig(
        files=['test_*.py'],
        functions=['test*'],
        classes=['Test*']
    )


class TestNode(object):

    def test_parse_should_return_a_node_instance(self, pattern_config):
        nodeid = 'tests/test_module.py::test_title'
        node = Node.parse(nodeid, pattern_config)

        assert isinstance(node, Node)

    def test_parse_should_parse_node_id_attributes(self, pattern_config):
        nodeid = 'tests/test_module.py::test_title'
        node = Node.parse(nodeid, pattern_config)

        assert node.title == formatters.format_title('test_title',
                                                     pattern_config.functions)
        assert node.module_name == (
            formatters.format_module_name('tests/test_module.py',
                                          pattern_config.files)
        )

    def test_parse_should_use_overwritten_title_instead_of_parse_node_id(
        self,
        pattern_config
    ):
        nodeid = 'tests/test_module.py::test_title'

        node = Node.parse(nodeid, pattern_config, overwrite_title='new title')

        assert node.title == 'new title'

    @pytest.mark.parametrize('nodeid,class_name', (
        ('tests/test_module.py::test_title', None),
        (
            'tests/test_module.py::TestClassName::()::test_title',
            formatters.format_class_name('TestClassName', ['Test*'])
        ),
        (
            'tests/test_module.py::TestClassName::test_title',
            formatters.format_class_name('TestClassName', ['Test*'])
        )
    ))
    def test_parse_with_class_name(self, pattern_config, nodeid, class_name):
        node = Node.parse(nodeid, pattern_config)

        assert node.class_name == class_name

    def test_repr_should_return_a_string_representation_of_itself(self, node):
        from_repr = eval(repr(node))

        assert from_repr.title == node.title
        assert from_repr.class_name == node.class_name
        assert from_repr.module_name == node.module_name

    def test_shoud_be_equal_when_objects_have_the_same_attributes(self, node):
        other = Node(
            title=node.title,
            class_name=node.class_name,
            module_name=node.module_name
        )

        assert node == other

    def test_should_not_be_equal_when_it_is_not_the_same_class(self, node):
        other = mock.Mock(
            title=node.title,
            class_name=node.class_name,
            module_name=node.module_name
        )

        assert node != other


class TestResult(object):

    @pytest.fixture
    def result(self, node):
        return Result('passed', node)

    def test_repr_should_return_a_string_representation_of_itself(
        self,
        node,
        result
    ):
        from_repr = eval(repr(result))

        assert from_repr.outcome == result.outcome
        assert isinstance(from_repr.node, Node)

    def test_create_should_return_a_result_with_a_parsed_node(
        self,
        report,
        pattern_config
    ):
        result = Result.create(report, pattern_config)

        assert isinstance(result, Result)
        assert result.outcome == report.outcome
        assert result.node == Node.parse(report.nodeid, pattern_config)
