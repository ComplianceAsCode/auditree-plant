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
"""Plant CLI tests."""

import json
import logging
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

from plant.cli import Plant


class TestPlantCLI(unittest.TestCase):
    """Test Plant CLI execution."""

    def setUp(self):
        """Initialize supporting test objects before each test."""
        logging.disable(logging.CRITICAL)
        self.plant = Plant()
        self.grc_patcher = patch('git.Repo.clone_from')
        self.git_repo_clone_from_mock = self.grc_patcher.start()
        self.git_remote_push_mock = MagicMock()
        git_remote_mock = MagicMock()
        git_remote_mock.push = self.git_remote_push_mock
        git_remotes_mock = MagicMock()
        git_remotes_mock.__getitem__ = MagicMock(return_value=git_remote_mock)
        git_config_parser_mock = MagicMock()
        git_config_parser_mock.get_value = MagicMock(return_value='finkel')
        repo_mock = MagicMock()
        repo_mock.config_reader = MagicMock(
            return_value=git_config_parser_mock
        )
        repo_mock.remotes = git_remotes_mock
        self.git_repo_clone_from_mock.return_value = repo_mock
        self.lic_patcher = patch('compliance.locker.Locker.init_config')
        self.locker_init_config_mock = self.lic_patcher.start()
        self.lci_patcher = patch('compliance.locker.Locker.checkin')
        self.locker_checkin_mock = self.lci_patcher.start()
        self.lae_patcher = patch('compliance.locker.Locker.add_evidence')
        self.locker_add_evidence_mock = self.lae_patcher.start()
        self.srm_patcher = patch('plant.cli.shutil.rmtree')
        self.shutil_rmtree_mock = self.srm_patcher.start()
        self.dry_run = [
            'dry-run',
            'https://github.com/foo/bar',
            '--creds',
            './test/fixtures/faux_creds.ini'
        ]
        self.push_remote = ['push-remote'] + self.dry_run[1:]

    def tearDown(self):
        """Cleanup supporting test objects after each test."""
        logging.disable(logging.NOTSET)
        self.grc_patcher.stop()
        self.lic_patcher.stop()
        self.lci_patcher.stop()
        self.lae_patcher.stop()
        self.srm_patcher.stop()

    def test_no_config_validation(self):
        """Ensures processing stops when no evidence config is provided."""
        self.plant.run(self.push_remote)
        self.git_repo_clone_from_mock.assert_not_called()
        self.locker_init_config_mock.assert_not_called()
        self.locker_add_evidence_mock.assert_not_called()
        self.locker_checkin_mock.assert_not_called()
        self.git_remote_push_mock.assert_not_called()
        self.shutil_rmtree_mock.assert_not_called()

    def test_multiple_config_validation(self):
        """Ensures processing stops when both config and path provided."""
        self.plant.run(
            self.push_remote + [
                '--config',
                json.dumps({'foo': 'bar'}),
                '--config-file',
                'foo/bar/baz_cfg.json'
            ]
        )
        self.git_repo_clone_from_mock.assert_not_called()
        self.locker_init_config_mock.assert_not_called()
        self.locker_add_evidence_mock.assert_not_called()
        self.locker_checkin_mock.assert_not_called()
        self.git_remote_push_mock.assert_not_called()
        self.shutil_rmtree_mock.assert_not_called()

    def test_multiple_git_config_validation(self):
        """Ensures processing stops when both git-config and path provided."""
        self.plant.run(
            self.push_remote + [
                '--git-config',
                json.dumps({'foo': 'bar'}),
                '--git-config-file',
                'foo/bar/baz_cfg.json'
            ]
        )
        self.git_repo_clone_from_mock.assert_not_called()
        self.locker_init_config_mock.assert_not_called()
        self.locker_add_evidence_mock.assert_not_called()
        self.locker_checkin_mock.assert_not_called()
        self.git_remote_push_mock.assert_not_called()
        self.shutil_rmtree_mock.assert_not_called()

    def test_dry_run_config(self):
        """Ensures dry-run mode works when config JSON is provided."""
        config = {
            '/home/foo/bar.json': {
                'category': 'foo', 'description': 'meh'
            }
        }
        with patch('plant.cli.open', mock_open(read_data='{}')):
            self.plant.run(self.dry_run + ['--config', json.dumps(config)])
        self.git_repo_clone_from_mock.assert_called_once_with(
            'https://1a2b3c4d5e6f7g8h9i0@github.com/foo/bar',
            f'{tempfile.gettempdir()}/plant',
            branch='master'
        )
        self.locker_init_config_mock.assert_called_once()
        self.locker_add_evidence_mock.assert_called_once()
        self.git_remote_push_mock.assert_not_called()
        self.shutil_rmtree_mock.assert_not_called()

    def test_dry_run_config_file(self):
        """Ensures dry-run mode works when a config file is provided."""
        config_file = './test/fixtures/faux_config.json'
        config_content = open(config_file).read()
        with patch('plant.cli.open', mock_open(read_data=config_content)):
            self.plant.run(self.dry_run + ['--config-file', config_file])
        self.git_repo_clone_from_mock.assert_called_once_with(
            'https://1a2b3c4d5e6f7g8h9i0@github.com/foo/bar',
            f'{tempfile.gettempdir()}/plant',
            branch='master'
        )
        self.locker_init_config_mock.assert_called_once()
        self.locker_add_evidence_mock.assert_called_once()
        self.git_remote_push_mock.assert_not_called()
        self.shutil_rmtree_mock.assert_not_called()

    def test_dry_run_git_config(self):
        """Ensures dry-run mode works when a git config is provided."""
        config = {
            '/home/foo/bar.json': {
                'category': 'foo', 'description': 'meh'
            }
        }
        git_config = {
            'commit': {
                'gpgsign': True
            },
            'user': {
                'signingKey': '...', 'email': '...', 'name': '...'
            }
        }
        with patch('plant.cli.open', mock_open(read_data='{}')):
            self.plant.run(
                self.dry_run + [
                    '--config',
                    json.dumps(config),
                    '--git-config',
                    json.dumps(git_config)
                ]
            )
        self.git_repo_clone_from_mock.assert_called_once_with(
            'https://1a2b3c4d5e6f7g8h9i0@github.com/foo/bar',
            f'{tempfile.gettempdir()}/plant',
            branch='master'
        )
        self.locker_init_config_mock.assert_called_once()
        self.locker_add_evidence_mock.assert_called_once()
        self.git_remote_push_mock.assert_not_called()
        self.shutil_rmtree_mock.assert_not_called()

    def test_dry_run_git_config_file(self):
        """Ensures dry-run mode works when a git config file is provided."""
        config = {
            '/home/foo/bar.json': {
                'category': 'foo', 'description': 'meh'
            }
        }
        git_config_file = './test/fixtures/faux_git_config.json'
        git_config_content = open(git_config_file).read()
        with patch('plant.cli.open', mock_open(read_data=git_config_content)):
            self.plant.run(
                self.dry_run + [
                    '--config',
                    json.dumps(config),
                    '--git-config-file',
                    './test/fixtures/faux_git_config.json'
                ]
            )
        self.git_repo_clone_from_mock.assert_called_once_with(
            'https://1a2b3c4d5e6f7g8h9i0@github.com/foo/bar',
            f'{tempfile.gettempdir()}/plant',
            branch='master'
        )
        self.locker_init_config_mock.assert_called_once()
        self.locker_add_evidence_mock.assert_called_once()
        self.git_remote_push_mock.assert_not_called()
        self.shutil_rmtree_mock.assert_not_called()

    @patch('git.Repo')
    @patch('os.path.isdir')
    def test_repo_path(self, isdir_mock, repo_mock):
        """Ensures providing a repo path does not clone a remote repo."""
        isdir_mock.return_value = True
        repo_mock.return_value = 'REPO'
        config = {
            '/home/foo/bar.json': {
                'category': 'foo', 'description': 'meh'
            }
        }
        with patch('plant.cli.open', mock_open(read_data='{}')):
            self.plant.run(
                self.dry_run
                + ['--config', json.dumps(config), '--repo-path', '/tmp/meh']
            )
        self.git_repo_clone_from_mock.assert_not_called()
        self.locker_init_config_mock.assert_called_once()
        self.locker_add_evidence_mock.assert_called_once()
        self.git_remote_push_mock.assert_not_called()
        self.shutil_rmtree_mock.assert_not_called()

    def test_push_remote(self):
        """
        Ensures push-remote mode works as expected.

        No other tests needed for push-remote since push-remote and dry-run
        use the same core plant command logic.
        """
        config = {
            '/home/foo/bar.json': {
                'category': 'foo', 'description': 'meh'
            }
        }
        with patch('plant.cli.open', mock_open(read_data='{}')):
            self.plant.run(self.push_remote + ['--config', json.dumps(config)])
        self.git_repo_clone_from_mock.assert_called_once_with(
            'https://1a2b3c4d5e6f7g8h9i0@github.com/foo/bar',
            f'{tempfile.gettempdir()}/plant',
            branch='master'
        )
        self.locker_init_config_mock.assert_called_once()
        self.locker_add_evidence_mock.assert_called_once()
        self.git_remote_push_mock.assert_called_once()
        self.shutil_rmtree_mock.assert_not_called()
