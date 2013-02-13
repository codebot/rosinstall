# Software License Agreement (BSD License)
#
# Copyright (c) 2009, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import unicode_literals

import os
import sys
from test.io_wrapper import StringIO
import unittest
import subprocess
import tempfile

import rosinstall
import rosinstall.helpers
import rosinstall.rosws_cli
from rosinstall.rosws_cli import RoswsCLI
from rosinstall.rosinstall_cli import rosinstall_main
from rosinstall.rosws_cli import rosws_main

import test.scm_test_base
from test.scm_test_base import AbstractSCMTest, _add_to_file, _nth_line_split


def create_svn_repo(test_root_path, remote_path, filler_path, svn_uri):
    # create a "remote" repo
    subprocess.check_call(["svnadmin", "create", remote_path], cwd=test_root_path)
    subprocess.check_call(["svn", "checkout", svn_uri, filler_path], cwd=test_root_path)
    subprocess.check_call(["touch", "fixed.txt"], cwd=filler_path)
    subprocess.check_call(["touch", "modified.txt"], cwd=filler_path)
    subprocess.check_call(["touch", "modified-fs.txt"], cwd=filler_path)
    subprocess.check_call(["touch", "deleted.txt"], cwd=filler_path)
    subprocess.check_call(["touch", "deleted-fs.txt"], cwd=filler_path)
    subprocess.check_call(["svn", "add", "fixed.txt"], cwd=filler_path)
    subprocess.check_call(["svn", "add", "modified.txt"], cwd=filler_path)
    subprocess.check_call(["svn", "add", "modified-fs.txt"], cwd=filler_path)
    subprocess.check_call(["svn", "add", "deleted.txt"], cwd=filler_path)
    subprocess.check_call(["svn", "add", "deleted-fs.txt"], cwd=filler_path)
    subprocess.check_call(["svn", "commit", "-m", "modified"], cwd=filler_path)


def modify_svn_repo(clone_path):
    # make local modifications
    subprocess.check_call(["rm", "deleted-fs.txt"], cwd=clone_path)
    subprocess.check_call(["svn", "rm", "deleted.txt"], cwd=clone_path)

    #_add_to_file(os.path.join(clone_path, "modified-fs.txt"), "foo\n")
    _add_to_file(os.path.join(clone_path, "modified.txt"), "foo\n")
    _add_to_file(os.path.join(clone_path, "added-fs.txt"), "tada\n")
    _add_to_file(os.path.join(clone_path, "added.txt"), "flam\n")
    subprocess.check_call(["svn", "add", "--no-auto-props", "added.txt"], cwd=clone_path)


class RosinstallDiffSvnTest(AbstractSCMTest):

    @classmethod
    def setUpClass(self):
        AbstractSCMTest.setUpClass()
        remote_path = os.path.join(self.test_root_path, "remote")
        filler_path = os.path.join(self.test_root_path, "filler")

        svn_uri = "file://localhost" + remote_path

        create_svn_repo(self.test_root_path, remote_path, filler_path, svn_uri)

        # rosinstall the remote repo and fake ros
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), "- other: {local-name: ../ros}\n- svn: {local-name: clone, uri: '" + svn_uri + "'}")

        cmd = ["rosinstall", "ws", "-n"]
        os.chdir(self.test_root_path)
        rosinstall_main(cmd)
        clone_path = os.path.join(self.local_path, "clone")

        modify_svn_repo(clone_path)

    def check_diff_output(self, output):
        # svn output order varies between versions
        expected = ["""\
Index: clone/added.txt
===================================================================
--- clone/added.txt\t(revision 0)\n+++ clone/added.txt\t(revision 0)
@@ -0,0 +1 @@
+flam""",
                    """\
Index: clone/modified.txt
===================================================================
--- clone/modified.txt\t(revision 1)
+++ clone/modified.txt\t(working copy)
@@ -0,0 +1 @@
+foo"""]
        for snippet in expected:
            self.assertTrue(snippet in output, output)

    def test_Rosinstall_diff_svn_outside(self):
        """Test diff output for svn when run outside workspace"""
        cmd = ["rosinstall", "ws", "--diff"]
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosinstall_main(cmd)
        sys.stdout = sys.__stdout__
        output = output.getvalue()
        self.check_diff_output(output)

        cmd = ["rosws", "diff", "-t", "ws"]
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        sys.stdout = sys.__stdout__
        output = output.getvalue()
        self.check_diff_output(output)

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_diff(os.path.join(self.test_root_path, 'ws'), []))

    def test_Rosinstall_diff_svn_inside(self):
        """Test diff output for svn when run inside workspace"""
        directory = self.test_root_path + "/ws"
        cmd = ["rosinstall", ".", "--diff"]
        os.chdir(directory)
        sys.stdout = output = StringIO()
        rosinstall_main(cmd)
        output = output.getvalue()
        self.check_diff_output(output)

        cmd = ["rosws", "diff"]
        os.chdir(directory)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        output = output.getvalue()
        sys.stdout = sys.__stdout__
        self.check_diff_output(output)

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_status(directory, []))

    def test_Rosinstall_status_svn_inside(self):
        """Test status output for svn when run inside workspace"""
        directory = self.test_root_path + "/ws"
        cmd = ["rosinstall", ".", "--status"]
        os.chdir(directory)
        sys.stdout = output = StringIO()
        rosinstall_main(cmd)
        output = output.getvalue()
        self.assertStatusListEqual('A       clone/added.txt\nD       clone/deleted.txt\n!       clone/deleted-fs.txt\nM       clone/modified.txt\n', output)

        cmd = ["rosws", "status"]
        os.chdir(directory)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        output = output.getvalue()
        sys.stdout = sys.__stdout__

        self.assertStatusListEqual('A       clone/added.txt\nD       clone/deleted.txt\n!       clone/deleted-fs.txt\nM       clone/modified.txt\n', output)

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_diff(directory, []))

    def test_Rosinstall_status_svn_outside(self):
        """Test status output for svn when run outside workspace"""
        cmd = ["rosinstall", "ws", "--status"]
        cmd = ["rosinstall", "ws", "--status"]
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosinstall_main(cmd)
        sys.stdout = output = StringIO()
        rosinstall_main(cmd)
        sys.stdout = sys.__stdout__
        output = output.getvalue()
        self.assertStatusListEqual('A       clone/added.txt\nD       clone/deleted.txt\n!       clone/deleted-fs.txt\nM       clone/modified.txt\n', output)

        cmd = ["rosws", "status", "-t", "ws"]
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        sys.stdout = sys.__stdout__
        output = output.getvalue()
        self.assertStatusListEqual('A       clone/added.txt\nD       clone/deleted.txt\n!       clone/deleted-fs.txt\nM       clone/modified.txt\n', output)

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_status(os.path.join(self.test_root_path, 'ws'), []))

    def test_Rosinstall_status_svn_untracked(self):
        """Test status output for svn when run outside workspace"""
        cmd = ["rosinstall", "ws", "--status-untracked"]
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosinstall_main(cmd)
        sys.stdout = sys.__stdout__
        output = output.getvalue()
        self.assertStatusListEqual('?       clone/added-fs.txt\nA       clone/added.txt\nD       clone/deleted.txt\n!       clone/deleted-fs.txt\nM       clone/modified.txt\n', output)

        cmd = ["rosws", "status", "-t", "ws", "--untracked"]
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        sys.stdout = sys.__stdout__
        output = output.getvalue()
        self.assertStatusListEqual('?       clone/added-fs.txt\nA       clone/added.txt\nD       clone/deleted.txt\n!       clone/deleted-fs.txt\nM       clone/modified.txt\n', output)

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_status(os.path.join(self.test_root_path, 'ws'), ["--untracked"]))

    def test_rosws_info_svn(self):
        cmd = ["rosws", "info", "-t", "ws"]
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        output = output.getvalue()
        tokens = _nth_line_split(-2, output)
        self.assertEqual(['clone', 'M', 'svn'], tokens[0:3])

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_info(os.path.join(self.test_root_path, 'ws'), []))


class RosinstallInfoSvnTest(AbstractSCMTest):

    def setUp(self):
        AbstractSCMTest.setUp(self)
        remote_path = os.path.join(self.test_root_path, "remote")
        filler_path = os.path.join(self.test_root_path, "filler")
        self.svn_uri = "file://localhost" + remote_path

        # create a "remote" repo
        subprocess.check_call(["svnadmin", "create", remote_path], cwd=self.test_root_path)
        subprocess.check_call(["svn", "checkout", self.svn_uri, filler_path], cwd=self.test_root_path)
        subprocess.check_call(["touch", "test.txt"], cwd=filler_path)
        subprocess.check_call(["svn", "add", "test.txt"], cwd=filler_path)
        subprocess.check_call(["svn", "commit", "-m", "modified"], cwd=filler_path)
        subprocess.check_call(["touch", "test2.txt"], cwd=filler_path)
        subprocess.check_call(["svn", "add", "test2.txt"], cwd=filler_path)
        subprocess.check_call(["svn", "commit", "-m", "modified"], cwd=filler_path)

        self.version_init = "-r1"
        self.version_end = "-r2"

        # rosinstall the remote repo and fake ros
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), "- other: {local-name: ../ros}\n- svn: {local-name: clone, uri: '" + self.svn_uri + "'}")

        cmd = ["rosws", "update"]
        os.chdir(self.local_path)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        output = output.getvalue()
        sys.stdout = sys.__stdout__

    def test_rosinstall_detailed_locapath_info(self):
        cmd = ["rosws", "info", "-t", "ws"]
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        output = output.getvalue()
        tokens = _nth_line_split(-2, output)
        self.assertEqual(['clone', 'svn', self.version_end, self.svn_uri], tokens)

        clone_path = os.path.join(self.local_path, "clone")
        # make local modifications check
        subprocess.check_call(["touch", "test3.txt"], cwd=clone_path)
        subprocess.check_call(["svn", "add", "test3.txt"], cwd=clone_path)
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        output = output.getvalue()
        tokens = _nth_line_split(-2, output)
        self.assertEqual(['clone', 'M', 'svn', self.version_end, self.svn_uri], tokens)

        subprocess.check_call(["rm", ".rosinstall"], cwd=self.local_path)
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), "- other: {local-name: ../ros}\n- svn: {local-name: clone, uri: '" + self.svn_uri + "', version: \"1\"}")
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        output = output.getvalue()
        tokens = _nth_line_split(-2, output)
        self.assertEqual(['clone', 'MV', 'svn', '1', self.version_end, "(%s)" % self.version_init, self.svn_uri], tokens)

        subprocess.check_call(["rm", "-rf", "clone"], cwd=self.local_path)
        os.chdir(self.test_root_path)
        sys.stdout = output = StringIO()
        rosws_main(cmd)
        output = output.getvalue()
        tokens = _nth_line_split(-2, output)
        self.assertEqual(['clone', 'x', 'svn', '1', self.svn_uri], tokens)
