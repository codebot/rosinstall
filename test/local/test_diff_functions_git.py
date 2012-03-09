import copy
import rosinstall.rosws_cli
from rosinstall.rosws_cli import RoswsCLI
from test.scm_test_base import AbstractSCMTest, _add_to_file, ROSINSTALL_CMD, ROSWS_CMD, _nth_line_split



        self.assertEqual('diff --git clone/added.txt clone/added.txt\nnew file mode 100644\nindex 0000000..8d63207\n--- /dev/null\n+++ clone/added.txt\n@@ -0,0 +1 @@\n+flam\ndiff --git clone/deleted-fs.txt clone/deleted-fs.txt\ndeleted file mode 100644\nindex e69de29..0000000\ndiff --git clone/deleted.txt clone/deleted.txt\ndeleted file mode 100644\nindex e69de29..0000000\ndiff --git clone/modified-fs.txt clone/modified-fs.txt\nindex e69de29..257cc56 100644\n--- clone/modified-fs.txt\n+++ clone/modified-fs.txt\n@@ -0,0 +1 @@\n+foo\ndiff --git clone/modified.txt clone/modified.txt\nindex e69de29..257cc56 100644\n--- clone/modified.txt\n+++ clone/modified.txt\n@@ -0,0 +1 @@\n+foo', output.rstrip())

        cmd = [ROSINSTALL_CMD, "ws", "--diff"]
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        output=call.communicate()[0]
        self.check_diff_output(output)

        cmd = [ROSWS_CMD, "diff", "-t", "ws"]

        cli = RoswsCLI()
        self.assertEqual(0,cli.cmd_diff(os.path.join(self.test_root_path, 'ws'), []))

        cmd = [ROSINSTALL_CMD, ".", "--diff"]
        self.check_diff_output(output)
        cmd = [ROSWS_CMD, "diff"]
        call = subprocess.Popen(cmd, cwd=directory, stdout=subprocess.PIPE)
        output=call.communicate()[0]

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_status(directory, []))


        cmd = [ROSINSTALL_CMD, ".", "--status"]

        cmd = [ROSWS_CMD, "status"]
        call = subprocess.Popen(cmd, cwd=directory, stdout=subprocess.PIPE)
        output=call.communicate()[0]
        self.assertEqual('A       clone/added.txt\n D      clone/deleted-fs.txt\nD       clone/deleted.txt\n M      clone/modified-fs.txt\nM       clone/modified.txt\n\n', output)

        cli = RoswsCLI()
        self.assertEqual(0,cli.cmd_diff(directory, []))

        cmd = [ROSINSTALL_CMD, "ws", "--status"]
        cmd = [ROSWS_CMD, "status", "-t", "ws"]
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        output=call.communicate()[0]
        self.assertEqual('A       clone/added.txt\n D      clone/deleted-fs.txt\nD       clone/deleted.txt\n M      clone/modified-fs.txt\nM       clone/modified.txt\n\n', output)

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_status(os.path.join(self.test_root_path, 'ws'), []))

        cmd = [ROSINSTALL_CMD, "ws", "--status-untracked"]
        cmd = [ROSWS_CMD, "status", "-t", "ws", "--untracked"]
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        output=call.communicate()[0]
        self.assertEqual('A       clone/added.txt\n D      clone/deleted-fs.txt\nD       clone/deleted.txt\n M      clone/modified-fs.txt\nM       clone/modified.txt\n??      clone/added-fs.txt\n\n', output)

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_status(os.path.join(self.test_root_path, 'ws'), ["--untracked"]))


    def test_rosws_info_git(self):
        """Test untracked status output for git"""

        cmd = [ROSWS_CMD, "info", "-t", "ws"]
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        output = call.communicate()[0]
        tokens = _nth_line_split(-2, output)
        self.assertEqual(['clone', 'M', 'git'], tokens[0:3])
        tokens2 = _nth_line_split(-1, output)
        self.assertEqual(1, len(tokens2))
        self.assertEqual('../ros', tokens2[0])

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_info(os.path.join(self.test_root_path, 'ws'), []))


class RosinstallInfoGitTest(AbstractSCMTest):

    def setUp(self):
	AbstractSCMTest.setUp(self)
	remote_path = os.path.join(self.test_root_path, "remote")
	os.makedirs(remote_path)

	# create a "remote" repo
	subprocess.check_call(["git", "init"], cwd=remote_path)
	subprocess.check_call(["touch", "test.txt"], cwd=remote_path)
	subprocess.check_call(["git", "add", "*"], cwd=remote_path)
	subprocess.check_call(["git", "commit", "-m", "modified"], cwd=remote_path)
	po = subprocess.Popen(["git", "log", "-n", "1", "--pretty=format:\"%H\""], cwd=remote_path, stdout=subprocess.PIPE)
	self.version_init = po.stdout.read().rstrip('"').lstrip('"')[0:12]
	subprocess.check_call(["git", "tag", "footag"], cwd=remote_path)
	subprocess.check_call(["touch", "test2.txt"], cwd=remote_path)
	subprocess.check_call(["git", "add", "*"], cwd=remote_path)
	subprocess.check_call(["git", "commit", "-m", "modified"], cwd=remote_path)
	po = subprocess.Popen(["git", "log", "-n", "1", "--pretty=format:\"%H\""], cwd=remote_path, stdout=subprocess.PIPE)
	self.version_end = po.stdout.read().rstrip('"').lstrip('"')[0:12]

	# rosinstall the remote repo and fake ros
	_add_to_file(os.path.join(self.local_path, ".rosinstall"), u"- other: {local-name: ../ros}\n- git: {local-name: clone, uri: ../remote}")

	cmd = [ROSWS_CMD]
	cmd.extend(["install", "-y"])
	call = subprocess.Popen(cmd, cwd=self.local_path, stdout=subprocess.PIPE)
	output=call.communicate()[0]


    def test_rosinstall_detailed_locapath_info(self):
	cmd = [ROSWS_CMD]
        cmd.extend(["info", "-t", "ws"])
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)

        output = call.communicate()[0]
        tokens = _nth_line_split(-2, output)
        self.assertEqual(['clone', 'git', self.version_end, os.path.join(self.test_root_path, 'remote')], tokens, output)

        clone_path = os.path.join(self.local_path, "clone")
        # make local modifications check
        subprocess.check_call(["rm", "test2.txt"], cwd=clone_path)
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        tokens = _nth_line_split(-2, call.communicate()[0])
        self.assertEqual(['clone', 'M', 'git', self.version_end, os.path.join(self.test_root_path, 'remote')], tokens)

        subprocess.check_call(["rm", ".rosinstall"], cwd=self.local_path)
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), u"- other: {local-name: ../ros}\n- git: {local-name: clone, uri: ../remote, version: \"footag\"}")
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        tokens = _nth_line_split(-2, call.communicate()[0])
        self.assertEqual(['clone', 'MV', 'git', 'footag', self.version_end, "(%s)"%self.version_init, os.path.join(self.test_root_path, 'remote')], tokens)

        # using a denormalized local-name here
        subprocess.check_call(["rm", ".rosinstall"], cwd=self.local_path)
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), u"- other: {local-name: ../ros}\n- git: {local-name: clone/../clone, uri: ../remote, version: \"footag\"}")
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        tokens = _nth_line_split(-2, call.communicate()[0])
        self.assertEqual(['clone', 'MV', 'git', 'footag', self.version_end, "(%s)"%self.version_init, os.path.join(self.test_root_path, 'remote')], tokens)

        # using an absolute path to clone dir here
        subprocess.check_call(["rm", ".rosinstall"], cwd=self.local_path)
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), u"- other: {local-name: ../ros}\n- git: {local-name: '"+clone_path+"', uri: ../remote, version: \"footag\"}")
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        tokens = _nth_line_split(-2, call.communicate()[0])
        self.assertEqual([clone_path, 'MV', 'git', 'footag', self.version_end, "(%s)"%self.version_init, os.path.join(self.test_root_path, 'remote')], tokens)

        # using an absolute path here where relative path is shorter to display (also checks x for missing)
        subprocess.check_call(["rm", ".rosinstall"], cwd=self.local_path)
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), u"- other: {local-name: ../ros}\n- git: {local-name: '"+os.path.join(self.local_path, "../foo")+"', uri: ../remote, version: \"footag\"}")
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        tokens = _nth_line_split(-2, call.communicate()[0])