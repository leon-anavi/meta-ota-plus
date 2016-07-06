SUMMARY = "AGL SOTA Package Group"
DESCRIPTION = "A set of packages belong to GENIVI SOTA Project and OSTree"

LICENSE = "MIT"

inherit packagegroup

PACKAGES = " packagegroup-agl-sota "

ALLOW_EMPTY_${PN} = "1"

RDEPENDS_${PN} += "\
    ota-plus-client \
    ota-plus-demo-provision \
    ostree \
"
