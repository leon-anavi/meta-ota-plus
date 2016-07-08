#!/usr/bin/python

import argparse
import base64
import os
from os import listdir
from os.path import exists, join
import re
import string
from StringIO import StringIO
import subprocess
from tarfile import TarFile, TarInfo

class OtaPlusUpdate(object):
    '''
    Represents a single update that can be delivered over OTA+
    '''
    def __init__(self, delta_num, from_sha, to_sha):
        self._delta_num = delta_num
        self._from_sha = from_sha
        self._to_sha = to_sha
    def to_sha(self):
        return self._to_sha
    def delta_num(self):
        return self._delta_num
    def __eq__(self, other):
        # pylint: disable=W0212
        return (self._delta_num == other._delta_num and
                self._from_sha == other._from_sha and
                self._to_sha == other._to_sha)
    def __str__(self):
        return "delta-%d-%s-%s" % (self._delta_num, self._from_sha,
                                   self._to_sha)
    def is_earlier_than(self, other):
        '''
        Is this update logically before other
        '''
        # pylint: disable=W0212
        return self._delta_num < other._delta_num

    @staticmethod
    def parse_from_filename(packagename, filename):
        re_updates = re.compile("^" + packagename + "-delta(\\d+)-([^\\-]+)-([^\\-\\.]+)\\.tar.gz$")
        m = re_updates.match(filename)
        if m:
            delta_num = int(m.group(1))
            return OtaPlusUpdate(delta_num, m.group(2), m.group(3))
        else:
            return None

class UpdateOutputDirectory(object):
    '''
    Manages the update output directory.  Encodes and decodes file names like:
    minimal-delta0-empty-f9fec916c2b05805f22ced2564a0bf6a2f7bc253b242d5bbbb103d7b9f4a6ea1.tar.gz
    minimal-delta1-f9fec916c2b05805f22ced2564a0bf6a2f7bc253b242d5bbbb103d7b9f4a6ea1-069c6c7081016aeb05c173e3613cd2531527811eaa5c8e6a5a12eaedbaba1a72.tar.gz
    minimal-delta2-069c6c7081016aeb05c173e3613cd2531527811eaa5c8e6a5a12eaedbaba1a72-54e1e11ddbf33782f0cdc063cc18f22af5cb9d5f3ac0aa12f7dd06c597359636.tar.gz
    '''
    def __init__(self, path, packagename):
        self._path = path
        self._packagename = packagename
        if not exists(path):
            os.makedirs(path)
    def _latest_update(self):
        best = None
        for path in listdir(self._path):
            print "checking %s" % path
            up = OtaPlusUpdate.parse_from_filename(self._packagename, path)
            if up:
                if not best:
                    best = up
                elif best.is_earlier_than(up):
                    best = up
                else:
                    print "%s is old" % up
        return best
    def baseline_sha(self):
        '''
        Return the SHA of the most recent update
        '''
        latest = self._latest_update()
        if latest:
            return latest.to_sha()
        else:
            return None
    def next_output_filename(self, packagename, to_sha):
        latest = self._latest_update()
        if latest:
            from_sha = latest.to_sha()
            delta_num = latest.delta_num() + 1
        else:
            from_sha = 'empty'
            delta_num = 0
        filename = '%s-delta%d-%s-%s.tar.gz' % (packagename, delta_num, from_sha,
                                            to_sha)
        return join(self._path, filename)

def hexstring_to_binstring(hexst):
    ret = ""
    while(hexst):
        num = hexst[:2]
        hexst = hexst[2:]
        ret += chr(int(num, 16))
    return ret

def delta_folder_name(from_sha, to_sha):
    from_bin = hexstring_to_binstring(from_sha)
    to_bin = hexstring_to_binstring(to_sha)

    from_b64 = base64.b64encode(from_bin).rstrip("=").translate(string.maketrans('/', '_'))
    to_b64 = base64.b64encode(to_bin).rstrip("=").translate(string.maketrans('/', '_'))

    if from_b64:
        namestr = from_b64 + "-" + to_b64
    else:
        namestr = to_b64

    return namestr[:2] + "/" + namestr[2:]

class UpdateMetaData(object):
    fields = [
        'CONFIG_PACKAGE',
        'CONFIG_VERSION',
        'CONFIG_DELTA_TO',
        'CONFIG_PATH',
        'CONFIG_UNION',
        'CONFIG_DELTA_FROM',
    ]
    def __init__(self):
        # pylint: disable=W0201
        self.config_union = True
        self.config_delta_from = ''
        self.config_path = '/'
    def write_out(self):
        res = ""
        for field_name in self.fields:
            python_name = field_name.lower()
            res += "%s=%s\n" % (field_name, self.__dict__[python_name])
        return res

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--image', required=True,
                        help="Rootfs image tarball")
    parser.add_argument('-r', '--repo', required=True,
                        help="OSTree repository place update in")
    parser.add_argument('--small', action='store_true',
                        help="Exclude static delta from update package")
    parser.add_argument('-o', '--output', required=True,
                        help="Directory to store generated OTA+ updates")
    parser.add_argument('-p', '--packagename', required=True, help="Package name that serves as a branch name for OSTree")
    parser.add_argument('-v', '--packageversion', required=True, help="Package version")
    parser.add_argument('-n', '--installpath', default='/', help="Path to install the package on target device")
    parser.add_argument('-u', '--union', type=bool, default=True, help="If the package overwrites files in install path. Should be \"true\" or \"false\"")
    parser.add_argument('-m', '--message', default='', help="Commit message")
    args = parser.parse_args()

    if not exists(args.image):
        print "Image %s not found" % args.image
        return

    outputdirectory = UpdateOutputDirectory(packagename=args.packagename,
                                            path=args.output)

    #deltaprefix = args.packagename.translate(string.maketrans('/\\', '__'))
    #delta_num, delta_from, delta_to = find_last_delta(args.output,
    #                                                  deltaprefix)

    if not exists(args.repo):
        os.makedirs(args.repo)
        subprocess.check_call(["ostree", "--repo="+args.repo, "init", "--mode=archive-z2"])

    # commit
    to = subprocess.check_output(['ostree', '--repo='+args.repo, 'commit',
                                  '--subject=\"'+args.message+'\"',
                                  '--branch='+args.packagename,
                                  '--tree=tar='+args.image]).strip()

    delta_from = outputdirectory.baseline_sha()
    if not args.small:
        # generate static delta
        cmd = ["ostree", "--repo="+args.repo, "static-delta", "generate",
               '--empty', '--to='+to, "--inline", "--min-fallback-size=65536"]

        if delta_from:
            cmd.append('--from='+delta_from)
        else:
            cmd.append('--empty')
        subprocess.check_call(cmd)
        #deltafolder = delta_folder_name("" if (delta_num < 0) else delta_to, to)

    #shutil.copytree(args.repo+"/deltas/"+deltafolder[:2], tarfolder + "/" + deltafolder[:2])

    outputfilename = outputdirectory.next_output_filename(args.packagename, to)

    update_meta_data = UpdateMetaData()
    # pylint: disable=W0201
    update_meta_data.config_package = args.packagename
    update_meta_data.config_version = args.packageversion
    update_meta_data.config_delta_to = to
    update_meta_data.config_path = args.installpath
    update_meta_data.config_union = args.union
    if delta_from:
        update_meta_data.config_delta_from = delta_from

    with TarFile(outputfilename, 'w') as outputtar:
        metafile = update_meta_data.write_out()
        tarinfo = TarInfo('Meta.config')
        tarinfo.size = len(metafile)
        outputtar.addfile(tarinfo, StringIO(metafile))
        if not args.small:
            print "TODO: include static delta"
    print "Generated %s" % outputfilename

if __name__ == "__main__":
    main()

# vim: set expandtab tabstop=4 shiftwidth=4:
