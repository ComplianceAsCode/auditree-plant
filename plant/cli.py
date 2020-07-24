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
"""Plant command line interface."""

import json
import os
import shutil
import tempfile
from urllib.parse import urlparse

from compliance.evidence import ExternalEvidence, YEAR
from compliance.utils.credentials import Config

from ilcli import Command

from plant import __version__ as version
from plant.locker import PlantLocker


class _CorePlantCommand(Command):

    def _init_arguments(self):
        self.add_argument(
            'locker',
            help=(
                'the URL to the evidence locker repository, '
                'as an example https://github.com/my-org/my-repo'
            )
        )
        self.add_argument(
            '--creds',
            metavar='~/path/creds',
            help='the path to credentials file - defaults to %(default)s',
            default='~/.credentials'
        )
        self.add_argument(
            '--config',
            help=(
                'JSON evidence-path/detail pairs needed to plant evidence.  '
                'Evidence path must be the absolute path to the file.  The '
                'detail is a dictionary of category, ttl, and description.  '
                'Only the category is required.'
            ),
            type=json.loads,
            metavar=(
                '\'{"/absolute/path/to/my/evidence.ext":{"category":"foo",'
                '"ttl": 86400,"description":"this is my evidence"},...}\''
            ),
            default={}
        )
        self.add_argument(
            '--config-file',
            help='path to a file containing the files (with config) to plant',
            metavar='~/path/to/config_file.json',
            default=False
        )
        self.add_argument(
            '--git-config',
            help='JSON git configuration for signing commits',
            type=json.loads,
            metavar=(
                '\'{"commit":{"gpgsign": true},'
                '"user":{"signingKey":"...","email":"...","name":"..."}}\''
            ),
            default=False
        )
        self.add_argument(
            '--git-config-file',
            help=(
                'path to a file containing the '
                'git configuration for signing commits'
            ),
            metavar='~/path/to/git_config_file.json',
            default=False
        )
        self.add_argument(
            '--repo-path',
            help=(
                'the operating system location of a local git repository - '
                'if not provided, repo will be cloned to $TMPDIR/plant'
            ),
            metavar='~/path/evidence-locker',
            default=None
        )

    def _validate_arguments(self, args):
        parsed = urlparse(args.locker)
        if not (parsed.scheme and parsed.hostname and parsed.path):
            return (
                'ERROR: locker url must be of the form '
                'https://hostname/org/repo'
            )
        if bool(args.config) == bool(args.config_file):
            return 'ERROR: Provide either a --config or a --config-file.'
        if args.git_config and args.git_config_file:
            return (
                'ERROR: Provide either a --git-config or a --git-config-file.'
            )

    def _run(self, args):
        self.out(self.intro_msg)
        gitconfig = None
        if args.git_config or args.git_config_file:
            gitconfig = args.git_config or json.loads(
                open(args.git_config_file).read()
            )
        # self.name drives the Locker push mode.
        #   - dry-run translates to locker no-push mode
        #   - push-remote translates to locker full-remote mode
        locker_args = [
            args.locker, args.creds, self.name, gitconfig, args.repo_path
        ]
        files = args.config
        if not files:
            files = json.loads(open(args.config_file).read())
        with self._get_locker(*locker_args) as locker:
            self.out(f'Local locker location is {locker.local_path}')
            for file_path, details in files.items():
                evidence = ExternalEvidence(
                    file_path.rsplit('/', 1).pop(),
                    details['category'],
                    details.get('ttl', YEAR),
                    details.get('description', '')
                )
                evidence.set_content(open(file_path).read())
                locker.add_evidence(evidence)
                self.out(
                    f'\nEvidence {file_path} added to '
                    f'external/{details["category"]}, metadata applied...'
                )
        self.out(self.outro_msg)

    def _get_locker(self, repo, creds, mode, gitconfig=None, repo_path=None):
        locker_name = 'plant'
        if repo_path:
            locker_name = repo_path.rsplit('/', 1).pop()
        else:
            local_locker_path = f'{tempfile.gettempdir()}/{locker_name}'
            if os.path.isdir(local_locker_path):
                self.out('Local locker found...')
                self._remove_locker(local_locker_path)
            self.out(
                f'Cloning local locker for {repo}.  Depending on the '
                'size of your locker, this may take a while...'
            )
        return PlantLocker(
            name=locker_name,
            repo_url=repo,
            creds=Config(creds),
            do_push=True if mode == 'push-remote' else False,
            gitconfig=gitconfig,
            repo_path=repo_path
        )

    def _remove_locker(self, locker_path):
        self.out('Removing local locker...')
        shutil.rmtree(locker_path)
        self.out('Local locker has been removed...')


class DryRun(_CorePlantCommand):
    """Perform requested changes locally and show results of changes."""

    name = 'dry-run'
    intro_msg = 'This is a dry run.  Remote locker will not be updated...'
    outro_msg = 'Remote locker was not updated...'


class PushToRemote(_CorePlantCommand):
    """Perform requested changes and push to the remote repository."""

    name = 'push-remote'
    intro_msg = 'This is an official run.  Remote locker will be updated...'
    outro_msg = 'Remote locker was updated...'


class Plant(Command):
    """The plant CLI base command."""

    subcommands = [DryRun, PushToRemote]

    def _init_arguments(self):
        self.add_argument(
            '--version',
            help='the plant version',
            action='version',
            version=f'v{version}'
        )


def run():
    """Execute the plant CLI."""
    plant = Plant()
    exit(plant.run())


if __name__ == '__main__':
    run()
