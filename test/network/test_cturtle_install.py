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

import os
import copy
import subprocess

import rosinstall
import rosinstall.helpers
import rosinstall.config
from rosinstall.rosinstall_cli import rosinstall_main
from rosinstall.config_yaml import get_yaml_from_uri, get_path_specs_from_uri
from test.scm_test_base import AbstractRosinstallBaseDirTest
from test.network.distro_test_util import ros_found_in_yaml, ros_found_in_path_spec


class RosinstallCturtleTest(AbstractRosinstallBaseDirTest):

    @classmethod
    def setUpClass(self):
        AbstractRosinstallBaseDirTest.setUpClass()

    def tearDown(self):
        pass

    def test_get_path_specs_from_uri_from_url(self):
        url = "http://ros.org/rosinstalls/cturtle_base.rosinstall"
        path_specs = get_path_specs_from_uri(url)
        self.assertTrue(ros_found_in_path_spec(path_specs), "No ros element in cturtle")

    def test_get_yaml_from_uri_from_url(self):
        url = "http://ros.org/rosinstalls/cturtle_base.rosinstall"
        yaml_elements = get_yaml_from_uri(url)
        self.assertTrue(ros_found_in_yaml(yaml_elements), "No ros element in %s"%url)

    def test_source(self):
        """checkout into temp dir and test setup files"""
        cmd = copy.copy(self.rosinstall_fn)
        cmd.extend(['-j8', self.directory, 'http://ros.org/rosinstalls/cturtle_ros.rosinstall'])
        self.assertTrue(rosinstall_main(cmd))
        generated_rosinstall_filename = os.path.join(self.directory, ".rosinstall")
        self.assertTrue(os.path.exists(generated_rosinstall_filename))
        self.assertTrue(os.path.exists(os.path.join(self.directory, "ros")))
        self.assertTrue(os.path.exists(os.path.join(self.directory, "setup.sh")))
        self.assertTrue(os.path.exists(os.path.join(self.directory, "setup.bash")))
        subprocess.call(". %s" % os.path.join(self.directory, 'setup.sh') , shell=True, env=self.new_environ)
        subprocess.check_call(". %s" % os.path.join(self.directory, 'setup.bash'), shell=True, env=self.new_environ, executable='bash')
