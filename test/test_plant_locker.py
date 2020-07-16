# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Plant locker tests."""

import logging
import tempfile
import unittest
from unittest.mock import MagicMock, create_autospec, mock_open, patch

from compliance.evidence import ExternalEvidence

from plant.locker import PlantLocker


class TestPlantLocker(unittest.TestCase):
    """Test PlantLocker."""

    def setUp(self):
        """Initialize supporting test objects before each test."""
        logging.disable(logging.CRITICAL)
        self.mock_logger_error = MagicMock()
        self.mock_logger = create_autospec(logging.Logger)
        self.mock_logger.error = self.mock_logger_error
        self.ctime_patcher = patch('plant.locker.time.ctime')
        self.ctime_mock = self.ctime_patcher.start()
        self.ctime_mock.return_value = 'NOW'
        self.push_patcher = patch('compliance.locker.Locker.push')
        self.push_mock = self.push_patcher.start()
        self.checkin_patcher = patch('compliance.locker.Locker.checkin')
        self.checkin_mock = self.checkin_patcher.start()
        self.init_patcher = patch('compliance.locker.Locker.init')
        self.init_mock = self.init_patcher.start()

    def tearDown(self):
        """Cleanup supporting test objects after each test."""
        logging.disable(logging.NOTSET)
        self.ctime_patcher.stop()
        self.push_patcher.stop()
        self.checkin_patcher.stop()
        self.init_patcher.stop()

    def test_constructor(self):
        """Ensures a planted list attribute and local path is set."""
        locker = PlantLocker(name='repo-foo', repo_path='/foo/bar//baz')
        self.assertEqual(locker.local_path, '/foo/bar/baz')
        self.assertEqual(locker.planted, [])

    def test_custom_exit_no_push(self):
        """Ensures that the context manager exit routine does not run push."""
        with PlantLocker('repo-foo') as locker:
            locker.logger = self.mock_logger
            locker.planted = ['foo', 'bar', 'baz']
        self.mock_logger_error.assert_not_called()
        self.checkin_mock.assert_called_once_with(
            'Planted external evidence at local time NOW\n\nfoo\nbar\nbaz'
        )
        self.push_mock.assert_not_called()

    def test_custom_exit_push(self):
        """Ensures that the context manager exit routine runs push."""
        with PlantLocker('repo-foo') as locker:
            locker.logger = self.mock_logger
            locker.planted = ['foo', 'bar', 'baz']
            locker.repo_url_with_creds = 'my repo'
        self.mock_logger_error.assert_not_called()
        self.checkin_mock.assert_called_once_with(
            'Planted external evidence at local time NOW\n\nfoo\nbar\nbaz'
        )
        self.push_mock.assert_called_once()

    def test_custom_exit_error_logging(self):
        """Ensures that the context manager exit routine logs an exception."""
        with self.assertRaises(ValueError):
            with PlantLocker('repo-foo') as locker:
                locker.logger = self.mock_logger
                locker.planted = ['foo', 'bar', 'baz']
                locker.repo_url_with_creds = 'repo-foo-url'
                raise ValueError('meh')
        self.mock_logger_error.assert_called_once_with(
            "<class 'ValueError'> meh"
        )
        self.checkin_mock.assert_called_once_with(
            'Planted external evidence at local time NOW\n\nfoo\nbar\nbaz'
        )
        self.push_mock.assert_called_once()

    @patch('plant.locker.format_json')
    def test_locker_index_override(self, format_json_mock):
        """Ensures plant locker indexing works."""
        format_json_mock.return_value = 'formatted metadata'
        mo = mock_open()
        get_value_mock = MagicMock(return_value='this_guy')
        config_reader_mock = MagicMock()
        config_reader_mock.get_value = get_value_mock
        index_add_mock = MagicMock()
        index_mock = MagicMock()
        index_mock.add = index_add_mock
        repo_mock = MagicMock()
        repo_mock.config_reader = MagicMock(return_value=config_reader_mock)
        repo_mock.index = index_mock
        evidence = ExternalEvidence('foo.json', 'bar', description='meh')
        with patch('builtins.open', mo):
            with PlantLocker('repo-foo') as locker:
                locker = PlantLocker('repo-foo')
                locker.repo = repo_mock
                locker.commit_date = 'NOW'
                locker.index(evidence)
                self.assertEqual(locker.planted, ['external/bar/foo.json'])
        mo.assert_called_once_with(
            f'{tempfile.gettempdir()}/repo-foo/external/bar/index.json', 'w'
        )
        expected_meta = {
            'foo.json': {
                'last_update': 'NOW',
                'ttl': 31536000,
                'planted_by': 'this_guy',
                'description': 'meh'
            }
        }
        format_json_mock.assert_called_once_with(expected_meta)
        mo_handle = mo()
        mo_handle.write.assert_called_once_with('formatted metadata')
        index_add_mock.assert_called_once_with(
            [
                f'{tempfile.gettempdir()}/repo-foo/external/bar/index.json',
                f'{tempfile.gettempdir()}/repo-foo/external/bar/foo.json'
            ]
        )

    @patch('json.loads')
    @patch('os.path.exists')
    @patch('plant.locker.format_json')
    def test_locker_index_override_metadata_found(
        self, format_json_mock, exists_mock, json_loads_mock
    ):
        """Ensures plant locker indexing works when metadata is found."""
        format_json_mock.return_value = 'formatted metadata'
        exists_mock.return_value = True
        json_loads_mock.return_value = {'other_meta': 'SOME OTHER METADATA'}
        mo = mock_open()
        get_value_mock = MagicMock(return_value='this_guy')
        config_reader_mock = MagicMock()
        config_reader_mock.get_value = get_value_mock
        index_add_mock = MagicMock()
        index_mock = MagicMock()
        index_mock.add = index_add_mock
        repo_mock = MagicMock()
        repo_mock.config_reader = MagicMock(return_value=config_reader_mock)
        repo_mock.index = index_mock
        evidence = ExternalEvidence('foo.json', 'bar', description='meh')
        with patch('builtins.open', mo):
            with PlantLocker('repo-foo') as locker:
                locker = PlantLocker('repo-foo')
                locker.repo = repo_mock
                locker.commit_date = 'NOW'
                locker.index(evidence)
                self.assertEqual(locker.planted, ['external/bar/foo.json'])
        mo.assert_called_with(
            f'{tempfile.gettempdir()}/repo-foo/external/bar/index.json', 'w'
        )
        expected_meta = {
            'other_meta': 'SOME OTHER METADATA',
            'foo.json': {
                'last_update': 'NOW',
                'ttl': 31536000,
                'planted_by': 'this_guy',
                'description': 'meh'
            }
        }
        format_json_mock.assert_called_once_with(expected_meta)
        mo_handle = mo()
        mo_handle.write.assert_called_once_with('formatted metadata')
        index_add_mock.assert_called_once_with(
            [
                f'{tempfile.gettempdir()}/repo-foo/external/bar/index.json',
                f'{tempfile.gettempdir()}/repo-foo/external/bar/foo.json'
            ]
        )
