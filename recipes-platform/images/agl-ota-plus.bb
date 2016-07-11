require recipes-platform/images/agl-demo-platform.bb

DESCRIPTION = "AGL OTA Plus image currently contains a simple HMI, \
demos, RVI SOTA client and OSTree."

# 1 Gb of free space
IMAGE_ROOTFS_EXTRA_SPACE="1048576"

IMAGE_FEATURES_append = " \
    "

# add packages for SOTA
IMAGE_INSTALL_append = " \
    packagegroup-agl-sota \
    "
