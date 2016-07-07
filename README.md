# AGL Demo image with GENIVI SOTA Project and OSTree
## Building AGL
Follow the instructions below to buid AGL image that incldues GENIVI SOTA project and OSTree.

* Prepare Repo:
```
mkdir ~/bin
export PATH=~/bin:$PATH
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo
```
* Get all layers:
```
repo init -u https://gerrit.automotivelinux.org/gerrit/AGL/AGL-repo
repo sync
```
* Get layer meta-ota-plus:
```
git clone https://github.com/konsulko/meta-ota-plus.git
```
* Set up the development environment for QEMU:
```
source meta-agl/scripts/envsetup.sh qemux86-64
```
* Add layer meta-ota-plus to BBLAYERS in conf/bblayers.conf using your favorite text editor

* Add the following line to conf/local.conf to enable and lauch CES2016 home application at startup:

```
DISTRO_FEATURES_append = " ota-plus-apps"
```

* Build the AGL demo platform with GENIVI SOTA project, ostree, etc:
```
bitbake agl-ota-plus
```

## Running AGL in QEMU

* Execute the following command within the build direction to go to the directory with QEMU images:
```
cd tmp/deploy/images/qemux86-64/
```
* Execute the following command to run AGL in QEMU:
```
QEMU_AUDIO_DRV=pa; $HOME/agl/poky/scripts/runqemu
bzImage-qemux86-64.bin agl-ota-plus-qemux86-64.ext4
```
* Alternatively, execute the following command to run AGL in QEMUwith enabled VNC:
```
QEMU_AUDIO_DRV=pa; $HOME/agl/poky/scripts/runqemu bzImage-qemux86-64.bin agl-ota-plus-qemux86-64.ext4 qemuparams="-nographic -vnc :0"
```
