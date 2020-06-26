SHELL := /bin/bash

PYTHON_LIB_DIR?=/usr/lib/python3/dist-packages
BASH_COMPLETION_DIR?=/etc/bash_completion.d
BIN_DIR?=/usr/bin
DATA_DIR?=/usr/share
DOC_DIR?=/usr/share/doc
ICON_DIR?=/usr/share/icons
LIB_DIR?=/usr/lib
MAN_DIR?=/usr/share/man
SHARE_DIR?=/usr/share

FILES := $(shell find bibliothek/* -type f ! -path "**/__pycache__/*" ! -path "**/.git" ! -path "**/.gitignore" ! -path "**/LICENSE" ! -path "**/README.md")


ifdef VERBOSE
  Q :=
else
  Q := @
endif


clean:
	$(Q)rm -rf ./build
	$(Q)find bibliothek -name __pycache__ -exec rm -rf {} \;


print-%:
	@echo $*=$($*)


venv:
	$(Q)virtualenv -p /usr/bin/python3 .venv
	$(Q)( \
		source .venv/bin/activate; \
		pip install -r requirements.txt; \
	)
	$(Q)ln -fs ${PYTHON_LIB_DIR}/gi .venv/lib/python3*/site-packages/
	$(Q)ln -fs ${PYTHON_LIB_DIR}/dbus .venv/lib/python3*/site-packages/
	$(Q)for f in ${PYTHON_LIB_DIR}/_dbus*; do \
		ln -fs $$f .venv/lib/python3*/site-packages/; \
	done


test: .venv
	$(Q)( \
		source .venv/bin/activate; \
		cd bibliothek; \
		python manage.py test; \
	)


deb: test build/package/DEBIAN/control
	$(Q)fakeroot dpkg-deb -b build/package build/bibliothek.deb
	$(Q)lintian -Ivi --suppress-tags embedded-javascript-library build/bibliothek.deb

deb-sign: deb
	$(Q)dpkg-sig -s build/bibliothek.deb


install: bibliothek.bash-completion build/bin/bibliothek build/bin/gnome-search-provider build/conf/org.gnome.bibliothek.SearchProvider.desktop build/conf/org.gnome.bibliothek.SearchProvider.service.systemd build/conf/org.gnome.bibliothek.SearchProvider.service.dbus build/conf/org.gnome.bibliothek.SearchProvider.ini
	$(Q)install bibliothek.bash-completion ${BASH_COMPLETION_DIR}
	$(Q)install -Dm 0755 build/bin/bibliothek ${BIN_DIR}
	$(Q)install -Dm 0755 build/bin/gnome-search-provider ${SHARE_DIR}bibliothek/
	$(Q)for f in ${FILES}; do \
		install -Dm 0644 $$f ${SHARE_DIR}$$f ; \
	done
	$(Q)install -Dm 0644 bibliothek/bibliothek/static/images/bibliothek.svg ${ICON_DIR}hicolor/scalable/apps/
	$(Q)install -Dm 0644 bibliothek/bibliothek/static/images/bibliothek-symbolic.svg ${ICON_DIR}hicolor/symbolic/apps/
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.ini ${SHARE_DIR}gnome-shell/search-providers/
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.desktop ${SHARE_DIR}applications/
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.service.dbus ${SHARE_DIR}dbus-1/services/org.gnome.bibliothek.SearchProvider.service
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.service.systemd ${LIB_DIR}systemd/user/org.gnome.bibliothek.SearchProvider.service
	@echo "bibliothek install completed."


uninstall:
	$(Q)rm -r ${SHARE_DIR}bibliothek
	$(Q)rm ${BIN_DIR}bibliothek
	$(Q)rm ${BASH_COMPLETION_DIR}bibliothek.bash-completion

	$(Q)rm ${SHARE_DIR}gnome-shell/search-providers/org.gnome.bibliothek.SearchProvider.ini
	$(Q)rm ${SHARE_DIR}applications/org.gnome.bibliothek.SearchProvider.desktop
	$(Q)rm ${SHARE_DIR}dbus-1/services/org.gnome.bibliothek.SearchProvider.service.dbus
	$(Q)rm ${LIB_DIR}systemd/user/org.gnome.bibliothek.SearchProvider.service.systemd
	$(Q)rm ${ICON_DIR}hicolor/scalable/apps/bibliothek.svg
	$(Q)rm ${ICON_DIR}hicolor/symbolic/apps/bibliothek-symbolic.svg
	@echo "bibliothek uninstall completed."


build:
	$(Q)mkdir -p build


build/bin: build
	$(Q)mkdir -p build/bin


build/conf: build
	$(Q)mkdir -p build/conf


build/package/DEBIAN: build
	@mkdir -p build/package/DEBIAN


build/bin/bibliothek: build/bin
	@echo "#!/usr/bin/env bash" > build/bin/bibliothek
	@echo "${SHARE_DIR}/bibliothek/bibliothek.py \"$$""@\"" >> build/bin/bibliothek


build/bin/gnome-search-provider: build/bin
	@echo "#!/usr/bin/env bash" > build/bin/gnome-search-provider
	@echo "${SHARE_DIR}/bibliothek/.venv/bin/python3 ${SHARE_DIR}/bibliothek/gnome-search-provider.py \"$$""@\"" >> build/bin/gnome-search-provider


build/copyright: build
	$(Q)echo "Upstream-Name: bibliothek" > build/copyright
	$(Q)echo "Source: https://github.com/jnphilipp/bibliothek" >> build/copyright
	$(Q)echo "" >> build/copyright
	$(Q)echo "Files: *" >> build/copyright
	$(Q)echo "Copyright: 2016-2020 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>" >> build/copyright
	$(Q)echo "License: GPL-3+" >> build/copyright
	$(Q)echo " This program is free software: you can redistribute it and/or modify" >> build/copyright
	$(Q)echo " it under the terms of the GNU General Public License as published by" >> build/copyright
	$(Q)echo " the Free Software Foundation, either version 3 of the License, or" >> build/copyright
	$(Q)echo " any later version." >> build/copyright
	$(Q)echo "" >> build/copyright
	$(Q)echo " This program is distributed in the hope that it will be useful," >> build/copyright
	$(Q)echo " but WITHOUT ANY WARRANTY; without even the implied warranty of" >> build/copyright
	$(Q)echo " MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the" >> build/copyright
	$(Q)echo " GNU General Public License for more details." >> build/copyright
	$(Q)echo "" >> build/copyright
	$(Q)echo " You should have received a copy of the GNU General Public License" >> build/copyright
	$(Q)echo " along with this program. If not, see <http://www.gnu.org/licenses/>." >> build/copyright
	$(Q)echo " On Debian systems, the full text of the GNU General Public" >> build/copyright
	$(Q)echo " License version 3 can be found in the file" >> build/copyright
	$(Q)echo " '/usr/share/common-licenses/GPL-3'." >> build/copyright


build/copyright.h2m: build
	$(Q)echo "[COPYRIGHT]" > build/copyright.h2m
	$(Q)echo "This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version." >> build/copyright.h2m
	$(Q)echo "" >> build/copyright.h2m
	$(Q)echo "This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details." >> build/copyright.h2m
	$(Q)echo "" >> build/copyright.h2m
	$(Q)echo "You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/." >> build/copyright.h2m


build/changelog.Debian.gz: build
	$(Q)declare TAGS=(`git tag`); for ((i=$${#TAGS[@]};i>=0;i--)); do if [ $$i -eq 0 ]; then git log $${TAGS[$$i]} --no-merges --format="psync ($${TAGS[$$i]}-%h) unstable; urgency=medium%n%n  * %s%n    %b%n -- %an <%ae>  %aD%n" | sed "/^\s*$$/d" >> build/changelog; elif [ $$i -eq $${#TAGS[@]} ]; then git log $${TAGS[$$i-1]}..HEAD --no-merges --format="psync ($${TAGS[$$i-1]}-%h) unstable; urgency=medium%n%n  * %s%n    %b%n -- %an <%ae>  %aD%n" | sed "/^\s*$$/d" >> build/changelog; else git log $${TAGS[$$i-1]}..$${TAGS[$$i]} --no-merges --format="psync ($${TAGS[$$i]}-%h) unstable; urgency=medium%n%n  * %s%n    %b%n -- %an <%ae>  %aD%n" | sed "/^\s*$$/d" >> build/changelog; fi; done
	$(Q)cat build/changelog | gzip -n9 > build/changelog.Debian.gz


build/bibliothek.1.gz: build build/copyright.h2m
	$(Q)( \
		source .venv/bin/activate; \
		help2man ./bibliothek/bibliothek.py -i build/copyright.h2m -n "Manage Library." | gzip -n9 > build/bibliothek.1.gz; \
	)
	$(Q)LC_ALL=en_US.UTF-8 MANROFFSEQ='' MANWIDTH=80 man --warnings -E UTF-8 -l -Tutf8 -Z ./build/bibliothek.1.gz > /dev/null


build/conf/org.gnome.bibliothek.SearchProvider.desktop: build/conf
	@echo "[Desktop Entry]" > build/conf/org.gnome.bibliothek.SearchProvider.desktop
	@echo "Version=1.0" >> build/conf/org.gnome.bibliothek.SearchProvider.desktop
	@echo "Categories=GNOME;Science;Literature;" >> build/conf/org.gnome.bibliothek.SearchProvider.desktop
	@echo "Icon=bibliothek" >> build/conf/org.gnome.bibliothek.SearchProvider.desktop
	@echo "Name=bibliothek" >> build/conf/org.gnome.bibliothek.SearchProvider.desktop
	@echo "Comment=GNOME Shell search provider for bibliothek" >> build/conf/org.gnome.bibliothek.SearchProvider.desktop
	@echo "Terminal=true" >> build/conf/org.gnome.bibliothek.SearchProvider.desktop
	@echo "Type=Application" >> build/conf/org.gnome.bibliothek.SearchProvider.desktop
	@echo "OnlyShowIn=GNOME;" >> build/conf/org.gnome.bibliothek.SearchProvider.desktop
	@echo "Keywords=Library" >> build/conf/org.gnome.bibliothek.SearchProvider.desktop


build/conf/org.gnome.bibliothek.SearchProvider.service.systemd: build/conf
	@echo "[Unit]" > build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "Description=bibliothek search provider for GNOME Shell daemon" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "[Service]" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "Type=dbus" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "BusName=org.gnome.bibliothek.SearchProvider" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "ExecStart=${SHARE_DIR}bibliothek/gnome-search-provider" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd


build/conf/org.gnome.bibliothek.SearchProvider.service.dbus: build/conf
	@echo "[D-BUS Service]" > build/conf/org.gnome.bibliothek.SearchProvider.service.dbus
	@echo "Name=org.gnome.bibliothek.SearchProvider" >> build/conf/org.gnome.bibliothek.SearchProvider.service.dbus
	@echo "Exec=${SHARE_DIR}bibliothek/gnome-search-provider" >> build/conf/org.gnome.bibliothek.SearchProvider.service.dbus
	@echo "SystemdService=org.gnome.bibliothek.SearchProvider.service" >> build/conf/org.gnome.bibliothek.SearchProvider.service.dbus


build/conf/org.gnome.bibliothek.SearchProvider.ini: build/conf
	@echo "[Shell Search Provider]" >> build/conf/org.gnome.bibliothek.SearchProvider.ini
	@echo "DesktopId=org.gnome.bibliothek.SearchProvider.desktop" >> build/conf/org.gnome.bibliothek.SearchProvider.ini
	@echo "BusName=org.gnome.bibliothek.SearchProvider" >> build/conf/org.gnome.bibliothek.SearchProvider.ini
	@echo "ObjectPath=/org/gnome/bibliothek/SearchProvider" >> build/conf/org.gnome.bibliothek.SearchProvider.ini
	@echo "Version=2" >> build/conf/org.gnome.bibliothek.SearchProvider.ini


build/package/DEBIAN/md5sums: bibliothek.bash-completion build/bin/bibliothek build/bin/gnome-search-provider build/conf/org.gnome.bibliothek.SearchProvider.desktop build/conf/org.gnome.bibliothek.SearchProvider.service.systemd build/conf/org.gnome.bibliothek.SearchProvider.service.dbus build/conf/org.gnome.bibliothek.SearchProvider.ini build/copyright build/changelog.Debian.gz build/bibliothek.1.gz build/package/DEBIAN build/bin/bibliothek build/bin/gnome-search-provider

	$(Q)install -Dm 0755 build/bin/bibliothek build/package"${BIN_DIR}"/bibliothek
	$(Q)install -Dm 0755 build/bin/gnome-search-provider build/package"${SHARE_DIR}"/bibliothek/gnome-search-provider
	$(Q)for f in ${FILES}; do \
		install -Dm 0644 $$f build/package"${SHARE_DIR}"/bibliothek/$$f ; \
	done

	$(Q)install -Dm 0644 build/changelog.Debian.gz build/package"${DOC_DIR}"/bibliothek/changelog.Debian.gz
	$(Q)install -Dm 0644 build/copyright build/package"${DOC_DIR}"/bibliothek/copyright
	$(Q)install -Dm 0644 build/bibliothek.1.gz build/package"${MAN_DIR}"/man1/bibliothek.1.gz

	$(Q)install -Dm 0644 bibliothek/bibliothek/static/images/bibliothek.svg build/package"${ICON_DIR}"/hicolor/scalable/apps/bibliothek.svg
	$(Q)install -Dm 0644 bibliothek/bibliothek/static/images/bibliothek-symbolic.svg build/package"${ICON_DIR}"hicolor/symbolic/apps/bibliothek.svg
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.ini build/package"${SHARE_DIR}"/gnome-shell/search-providers/org.gnome.bibliothek.SearchProvider.ini
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.desktop build/package"${SHARE_DIR}"/applications/org.gnome.bibliothek.SearchProvider.desktop
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.service.dbus build/package"${SHARE_DIR}"/dbus-1/services/org.gnome.bibliothek.SearchProvider.service
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.service.systemd build/package"${LIB_DIR}"/systemd/user/org.gnome.bibliothek.SearchProvider.service

	$(Q)mkdir -p build/package/DEBIAN
	$(Q)find build/package -type f -not -path "*DEBIAN*" -exec md5sum {} \; > build/md5sums
	$(Q)sed -e "s/build\/package\///" build/md5sums > build/package/DEBIAN/md5sums
	$(Q)chmod 0644 build/package/DEBIAN/md5sums


build/package/DEBIAN/control: build/package/DEBIAN/md5sums
	$(Q)echo "Package: bibliothek" > build/package/DEBIAN/control
	$(Q)echo "Version: 0.1-`git log --format=%h -1`" >> build/package/DEBIAN/control
	$(Q)echo "Section: utils" >> build/package/DEBIAN/control
	$(Q)echo "Priority: optional" >> build/package/DEBIAN/control
	$(Q)echo "Architecture: all" >> build/package/DEBIAN/control
	$(Q)echo "Depends: python3 (<< 3.9), python3 (>= 3.6), python3:any, python3-gi, python3-django (= 2.2~), python3-bibtexparser (=1.1~), python3-feedparser (=5.2~)" >> build/package/DEBIAN/control
	$(Q)echo "Installed-Size: `du -sk build/package/usr | grep -oE "[0-9]+"`" >> build/package/DEBIAN/control
	$(Q)echo "Maintainer: J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>" >> build/package/DEBIAN/control
	$(Q)echo "Homepage: https://github.com/jnphilipp/bibliothek" >> build/package/DEBIAN/control
	$(Q)echo "Description: Library managing tool for the command line" >> build/package/DEBIAN/control
	$(Q)echo " This tool provides a command line interfaces to manage books with different" >> build/package/DEBIAN/control
	$(Q)echo " editions, magazines or scientific papers." >> build/package/DEBIAN/control
	$(Q)echo " It includes a search provider for the GNOME desktop." >> build/package/DEBIAN/control
