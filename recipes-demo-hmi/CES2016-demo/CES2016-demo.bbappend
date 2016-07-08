SRC_URI = "git://github.com/openivimobility/CES2016.git;protocol=ssh;branch=qemu"
S = "${WORKDIR}/git"

SRCREV = "6ac449529a2907967374540970c8fd705879f64a"

inherit systemd

do_install_append() {
 if ${@bb.utils.contains('DISTRO_FEATURES', 'systemd', 'true', 'false', d)} && ${@bb.utils.contains('DISTRO_FEATURES', 'ota-plus-apps', 'true', 'false', d)}; then
  # Execute these manually on behalf of systemctl script (from systemd-systemctl-native.bb)
  # to deploy demohmi systemd service because it does not support systemd's user mode.
  install -m 644 -p -D ${S}/scripts/demohmi.service ${D}${systemd_user_unitdir}/demohmi.service
  mkdir -p ${D}/${ROOT_HOME}/.config/systemd/user/default.target.wants/
  ln -sf ${systemd_user_unitdir}/demohmi.service ${D}/${ROOT_HOME}/.config/systemd/user/default.target.wants/demohmi.service
 fi
}

pkg_postinst_${PN} () {
#!/bin/sh -e
# Swith to Weston IVI shell
mv /etc/xdg/weston/weston.ini /etc/xdg/weston/weston.ini.desktop-shell
cp /opt/AGL/CES2016/weston.ini.ivi-shell /etc/xdg/weston/
ln -sf /etc/xdg/weston/weston.ini.ivi-shell /etc/xdg/weston/weston.ini
}

FILES_${PN} += " \
    ${@bb.utils.contains('DISTRO_FEATURES', 'ota-plus-apps', '${systemd_user_unitdir}/demohmi.service', '', d)} \
    ${@bb.utils.contains('DISTRO_FEATURES', 'ota-plus-apps', '${ROOT_HOME}/.config/systemd/user/default.target.wants/', '', d)} \
    ${@bb.utils.contains('DISTRO_FEATURES', 'ota-plus-apps', '${ROOT_HOME}/.config/systemd/user/default.target.wants/demohmi.service', '', d)} \
    "
