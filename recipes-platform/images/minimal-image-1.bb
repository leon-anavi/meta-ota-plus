DESCRIPTION = "Minimal OTA-Plus image"

IMAGE_ROOTFS_SIZE ?= "8192"

# 1GB of extra space
IMAGE_ROOTFS_EXTRA_SPACE = "1000000"

IMAGE_FEATURES += "splash package-management ssh-server-dropbear"

inherit core-image

IMAGE_INSTALL_append = " \
    connman \
    connman-tools \
    connman-client \
    packagegroup-agl-sota \
    "
