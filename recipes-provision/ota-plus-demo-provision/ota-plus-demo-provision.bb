DESCRIPTION = "Provision ota-plus-client"
LICENSE = "MIT | Apache-2.0"
LIC_FILES_CHKSUM = \
"file://${S}/README.md;beginline=1;endline=2;md5=fdbea5aa8e93e9429f32abe06722b2bc"

SRC_URI = "git://github.com/advancedtelematic/ota-plus-demo-provision;protocol=ssh;branch=master"
S = "${WORKDIR}/git"

SRCREV = "${AUTOREV}"

PV = "1.0+${SRCPV}"

inherit systemd

PR="4"

FILES_${PN} = " \
                /etc/ota/credentials/* \
                /var/lib/connman/* \
                /usr/bin/ota-plus-demo-provision \
                ${base_libdir}/systemd/system/ota-plus-client.service \
              "

SYSTEMD_SERVICE_${PN} = "ota-plus-demo-provision.service"

RDEPENDS_${PN} = "python"

do_install() {
  install -d ${D}${systemd_unitdir}/system
  install -c ${S}/ota-plus-demo-provision.service ${D}${systemd_unitdir}/system

  install -d ${D}${sysconfdir}/ota
  cp -r ${S}/credentials/ ${D}${sysconfdir}/ota/

  install -d ${D}${bindir}
  install -m 0755 ${S}/ota-plus-demo-provision ${D}${bindir}

  install -d ${D}${localstatedir}/lib/
  cp -r ${S}/connman/ ${D}${localstatedir}/lib/
}
