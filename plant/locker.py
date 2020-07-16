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
"""Plant Locker."""

import json
import os
import time

from compliance.locker import Locker
from compliance.utils.data_parse import format_json


class PlantLocker(Locker):
    """Provide plant specific locker functionality."""

    def __init__(
        self,
        name=None,
        repo_url=None,
        creds=None,
        do_push=False,
        gitconfig=None,
        repo_path=None
    ):
        """Plant locker constructor to add external evidence."""
        super().__init__(
            name=name,
            repo_url=repo_url,
            creds=creds,
            do_push=do_push,
            gitconfig=gitconfig
        )
        if repo_path is not None:
            self.local_path = os.path.normpath(repo_path)
        self.planted = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Override check in routine with a custom plant commit message."""
        if exc_type:
            self.logger.error(' '.join([str(exc_type), str(exc_val)]))
        planted_files = '\n'.join(self.planted)
        self.checkin(
            (
                'Planted external evidence at local time '
                f'{time.ctime(time.time())}\n\n{planted_files}'
            )
        )
        if self.repo_url_with_creds:
            self.push()
        return

    def index(self, evidence, checks=None, evidence_used=None):
        """
        Add external evidence to the git index.

        Overrides the base Locker index method called by add_evidence.
        """
        with self.lock:
            index_file = self.get_index_file(evidence)
            if not os.path.exists(index_file):
                metadata = {}
            else:
                metadata = json.loads(open(index_file).read())
            planter = self.repo.config_reader().get_value('user', 'email')
            metadata[evidence.name] = {
                'last_update': self.commit_date,
                'ttl': evidence.ttl,
                'planted_by': planter,
                'description': evidence.description
            }
            with open(index_file, 'w') as f:
                f.write(format_json(metadata))
            self.repo.index.add([index_file, self.get_file(evidence.path)])
            self.planted.append(evidence.path)
