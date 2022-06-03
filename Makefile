SHELL:=/bin/bash

PYTHON_LIB_DIR?=/usr/lib/python3/dist-packages
BASH_COMPLETION_DIR?=/usr/share/bash-completion.d
BIN_DIR?=/usr/bin
DATA_DIR?=/usr/share
DOC_DIR?=/usr/share/doc
ICON_DIR?=/usr/share/icons
LIB_DIR?=/usr/lib
MAN_DIR?=/usr/share/man
SHARE_DIR?=/usr/share
SYSTEMD_DIR?=/usr/lib/systemd/user
DEST_DIR?=
DJANGO?=

FILES := $(shell find bibliothek/* -type f ! -path "**/__pycache__/*" ! -path "**/.git" ! -path "**/.gitignore" ! -path "**/LICENSE" ! -path "**/README.md")


ifdef VERBOSE
  Q :=
else
  Q := @
endif

print-%:
	@echo $*=$($*)


clean:
	$(Q)rm -rf ./build
	$(Q)rm -rf ./bibliothek/static
	$(Q)find bibliothek -depth -name __pycache__ -type d -exec rm -rf {} \;


venv:
	$(Q)make .venv


.venv:
	$(Q)/usr/bin/python3 -m venv .venv
	$(Q)( \
		source .venv/bin/activate; \
		pip install --upgrade pip; \
		pip install django~=${DJANGO}; \
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


bibliothek/static: .venv
	$(Q)( \
		source .venv/bin/activate; \
		python bibliothek/manage.py collectstatic -c --noinput; \
	)


deb: test build/package/DEBIAN/control
	$(Q)fakeroot dpkg-deb -b build/package build/bibliothek.deb
	$(Q)lintian -Ivi --suppress-tags embedded-javascript-library build/bibliothek.deb
	$(Q)dpkg-sig -s builder build/bibliothek.deb
	@echo "bibliothek.deb completed."


install: bibliothek.bash-completion bibliothek/static build/bin/bibliothek build/bin/gnome-search-provider build/changelog.Debian.gz build/copyright build/bibliothek.1.gz build/conf/uwsgi.ini build/conf/bibliothek.desktop build/conf/org.gnome.bibliothek.SearchProvider.ini build/conf/org.gnome.bibliothek.SearchProvider.service.dbus build/conf/org.gnome.bibliothek.SearchProvider.service.systemd build/conf/bibliothek.service.systemd-user
	$(Q)for f in ${FILES}; do \
		install -Dm 0644 $$f "${DEST_DIR}${SHARE_DIR}"/$$f; \
	done
	$(Q)for f in $(shell find bibliothek/static/* -type f); do \
		install -Dm 0644 $$f "${DEST_DIR}${SHARE_DIR}"/$$f; \
	done
	$(Q)install -Dm 0644 build/conf/uwsgi.ini "${DEST_DIR}${SHARE_DIR}"/bibliothek/uwsgi.ini

	$(Q)install -Dm 0644 bibliothek.bash-completion "${DEST_DIR}/${BASH_COMPLETION_DIR}"/bibliothek.bash-completion
	$(Q)install -Dm 0755 build/bin/bibliothek "${DEST_DIR}/${BIN_DIR}"/bibliothek
	$(Q)install -Dm 0755 build/bin/gnome-search-provider "${DEST_DIR}/${SHARE_DIR}"/bibliothek/gnome-search-provider

	$(Q)install -Dm 0644 build/changelog.Debian.gz "${DEST_DIR}${DOC_DIR}"/bibliothek/changelog.Debian.gz
	$(Q)install -Dm 0644 build/copyright "${DEST_DIR}${DOC_DIR}"/bibliothek/copyright
	$(Q)install -Dm 0644 build/bibliothek.1.gz build/package"${MAN_DIR}"/man1/bibliothek.1.gz

	$(Q)install -Dm 0644 bibliothek/static/images/bibliothek.svg "${DEST_DIR}/${ICON_DIR}"/hicolor/scalable/apps/bibliothek.svg
	$(Q)install -Dm 0644 bibliothek/static/images/bibliothek-symbolic.svg "${DEST_DIR}/${ICON_DIR}"/hicolor/symbolic/apps/bibliothek.svg

	$(Q)install -Dm 0644 build/conf/bibliothek.desktop "${DEST_DIR}/${SHARE_DIR}"/applications/bibliothek.desktop
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.ini "${DEST_DIR}/${SHARE_DIR}"/gnome-shell/search-providers/org.gnome.bibliothek.SearchProvider.ini
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.service.dbus "${DEST_DIR}/${SHARE_DIR}"/dbus-1/services/org.gnome.bibliothek.SearchProvider.service
	$(Q)install -Dm 0644 build/conf/org.gnome.bibliothek.SearchProvider.service.systemd "${DEST_DIR}/${SYSTEMD_DIR}"/org.gnome.bibliothek.SearchProvider.service
	$(Q)install -Dm 0644 build/conf/bibliothek.service.systemd-user "${DEST_DIR}${SYSTEMD_DIR}"/bibliothek.service

	@echo "bibliothek install completed."


uninstall:
	$(Q)rm -r "${DEST_DIR}${SHARE_DIR}"/bibliothek
	$(Q)rm -r "${DEST_DIR}${DOC_DIR}"/bibliothek

	$(Q)rm "${DEST_DIR}${BIN_DIR}"/bibliothek
	$(Q)rm "${DEST_DIR}${BASH_COMPLETION_DIR}"/bibliothek.bash-completion

	$(Q)rm "${DEST_DIR}${SHARE_DIR}"/gnome-shell/search-providers/org.gnome.bibliothek.SearchProvider.ini
	$(Q)rm "${DEST_DIR}${SHARE_DIR}"/applications/bibliothek.desktop
	$(Q)rm "${DEST_DIR}${SHARE_DIR}"/dbus-1/services/org.gnome.bibliothek.SearchProvider.service

	$(Q)rm "${DEST_DIR}${SYSTEMD_DIR}"/bibliothek.service
	$(Q)rm "${DEST_DIR}${SYSTEMD_DIR}"/org.gnome.bibliothek.SearchProvider.service

	$(Q)rm "${DEST_DIR}${ICON_DIR}"/hicolor/scalable/apps/bibliothek.svg
	$(Q)rm "${DEST_DIR}${ICON_DIR}"/hicolor/symbolic/apps/bibliothek-symbolic.svg

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
	@echo "python3 ${SHARE_DIR}/bibliothek/bibliothek.py \"$$""@\"" >> build/bin/bibliothek


build/bin/gnome-search-provider: build/bin
	@echo "#!/usr/bin/env bash" > build/bin/gnome-search-provider
	@echo "python3 ${SHARE_DIR}/bibliothek/gnome-search-provider.py \"$$""@\"" >> build/bin/gnome-search-provider


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
	$(Q)( \
		declare TAGS=(`git tag`); \
		for ((i=$${#TAGS[@]};i>=0;i--)); do \
			if [ $$i -eq 0 ]; then \
				echo -e "bibliothek ($${TAGS[$$i]}) unstable; urgency=medium" >> build/changelog; \
				git log $${TAGS[$$i]} --no-merges --format="  * %h %s"  >> build/changelog; \
				git log $${TAGS[$$i]} -n 1 --format=" -- %an <%ae>  %aD" >> build/changelog; \
			elif [ $$i -eq $${#TAGS[@]} ] && [ $$(git log $${TAGS[$$i-1]}..HEAD --oneline | wc -l) -ne 0 ]; then \
				echo -e "bibliothek ($${TAGS[$$i-1]}-$$(git log -n 1 --format='%h')) unstable; urgency=medium" >> build/changelog; \
				git log $${TAGS[$$i-1]}..HEAD --no-merges --format="  * %h %s"  >> build/changelog; \
				git log HEAD -n 1 --format=" -- %an <%ae>  %aD" >> build/changelog; \
			elif [ $$i -lt $${#TAGS[@]} ]; then \
				echo -e "bibliothek ($${TAGS[$$i]}) unstable; urgency=medium" >> build/changelog; \
				git log $${TAGS[$$i-1]}..$${TAGS[$$i]} --no-merges --format="  * %h %s"  >> build/changelog; \
				git log $${TAGS[$$i]} -n 1 --format=" -- %an <%ae>  %aD" >> build/changelog; \
			fi; \
		done \
	)
	$(Q)cat build/changelog | gzip -n9 > build/changelog.Debian.gz


build/bibliothek.1.gz: build build/copyright.h2m
	$(Q)( \
		source .venv/bin/activate; \
		help2man ./bibliothek/bibliothek.py -i build/copyright.h2m -n "Manage books, papers and magazines." | gzip -n9 > build/bibliothek.1.gz; \
	)
	$(Q)LC_ALL=en_US.UTF-8 MANROFFSEQ='' MANWIDTH=80 man --warnings -E UTF-8 -l -Tutf8 -Z ./build/bibliothek.1.gz > /dev/null


build/conf/bibliothek.desktop: build/conf
	@echo "[Desktop Entry]" > build/conf/bibliothek.desktop
	@echo "Version=1.0" >> build/conf/bibliothek.desktop
	@echo "Categories=GNOME;Science;Literature;" >> build/conf/bibliothek.desktop
	@echo "Icon=bibliothek" >> build/conf/bibliothek.desktop
	@echo "Name=bibliothek" >> build/conf/bibliothek.desktop
	@echo "Comment=Manage books, papers and magazines" >> build/conf/bibliothek.desktop
	@echo "Terminal=false" >> build/conf/bibliothek.desktop
	@echo "Exec=xdg-open http://localhost:8081" >> build/conf/bibliothek.desktop
	@echo "Type=Application" >> build/conf/bibliothek.desktop
	@echo "OnlyShowIn=GNOME;" >> build/conf/bibliothek.desktop
	@echo "Keywords=Library" >> build/conf/bibliothek.desktop


build/conf/org.gnome.bibliothek.SearchProvider.service.systemd: build/conf
	@echo "[Unit]" > build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "Description=bibliothek search provider for GNOME Shell daemon" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "[Service]" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "Type=dbus" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "BusName=org.gnome.bibliothek.SearchProvider" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd
	@echo "ExecStart=${SHARE_DIR}/bibliothek/gnome-search-provider" >> build/conf/org.gnome.bibliothek.SearchProvider.service.systemd


build/conf/bibliothek.service.systemd-user: build/conf
	@echo "[Unit]" > build/conf/bibliothek.service.systemd-user
	@echo "Description=bibliothek uWSGI app" >> build/conf/bibliothek.service.systemd-user
	@echo "" >> build/conf/bibliothek.service.systemd-user
	@echo "[Service]" >> build/conf/bibliothek.service.systemd-user
	@echo "Type=simple" >> build/conf/bibliothek.service.systemd-user
	@echo "StandardOutput=journal" >> build/conf/bibliothek.service.systemd-user
	@echo "ExecStart=uwsgi --ini /usr/share/bibliothek/uwsgi.ini" >> build/conf/bibliothek.service.systemd-user
	@echo "Restart=on-failure" >> build/conf/bibliothek.service.systemd-user
	@echo "KillSignal=SIGQUIT" >> build/conf/bibliothek.service.systemd-user
	@echo "" >> build/conf/bibliothek.service.systemd-user
	@echo "[Install]" >> build/conf/bibliothek.service.systemd-user
	@echo "WantedBy=default.target" >> build/conf/bibliothek.service.systemd-user


build/conf/org.gnome.bibliothek.SearchProvider.service.dbus: build/conf
	@echo "[D-BUS Service]" > build/conf/org.gnome.bibliothek.SearchProvider.service.dbus
	@echo "Name=org.gnome.bibliothek.SearchProvider" >> build/conf/org.gnome.bibliothek.SearchProvider.service.dbus
	@echo "Exec=${SHARE_DIR}/bibliothek/gnome-search-provider" >> build/conf/org.gnome.bibliothek.SearchProvider.service.dbus
	@echo "SystemdService=org.gnome.bibliothek.SearchProvider.service" >> build/conf/org.gnome.bibliothek.SearchProvider.service.dbus


build/conf/org.gnome.bibliothek.SearchProvider.ini: build/conf
	@echo "[Shell Search Provider]" >> build/conf/org.gnome.bibliothek.SearchProvider.ini
	@echo "DesktopId=bibliothek.desktop" >> build/conf/org.gnome.bibliothek.SearchProvider.ini
	@echo "BusName=org.gnome.bibliothek.SearchProvider" >> build/conf/org.gnome.bibliothek.SearchProvider.ini
	@echo "ObjectPath=/org/gnome/bibliothek/SearchProvider" >> build/conf/org.gnome.bibliothek.SearchProvider.ini
	@echo "Version=2" >> build/conf/org.gnome.bibliothek.SearchProvider.ini


build/conf/uwsgi.ini: build/conf
	@echo "[uwsgi]" > build/conf/uwsgi.ini
	@echo "project      = bibliothek" >> build/conf/uwsgi.ini
	@echo "uid          = %u" >> build/conf/uwsgi.ini
	@echo "gid          = %g" >> build/conf/uwsgi.ini
	@echo "plugin       = python" >> build/conf/uwsgi.ini
	@echo "chdir        = ${SHARE_DIR}/%(project)" >> build/conf/uwsgi.ini
	@echo "module       = %(project).wsgi" >> build/conf/uwsgi.ini
	@echo "static-map   = /static=${SHARE_DIR}/%(project)/static" >> build/conf/uwsgi.ini
	@echo "static-map   = /media=$(HOME)/.local/share/%(project)" >> build/conf/uwsgi.ini
	@echo "protocol     = http" >> build/conf/uwsgi.ini
	@echo "master       = true" >> build/conf/uwsgi.ini
	@echo "processes    = 1" >> build/conf/uwsgi.ini
	@echo "socket       = :8081" >> build/conf/uwsgi.ini
	@echo "chown-socket = %(uid):%(gid)" >> build/conf/uwsgi.ini
	@echo "chmod-socket = 660" >> build/conf/uwsgi.ini
	@echo "vacuum       = true" >> build/conf/uwsgi.ini
	@echo "pidfile      = /tmp/uwsgi-%(uid)%(gid)_%(project).pid" >> build/conf/uwsgi.ini
	@echo "harakiri     = 20" >> build/conf/uwsgi.ini
	@echo "max-requests = 5000" >> build/conf/uwsgi.ini


build/package/DEBIAN/md5sums:
	$(Q)make install DEST_DIR=build/package
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
	$(Q)echo "Depends: python3 (<< 3.11), python3 (>= 3.7), python3:any, python3-gi, python3-django (= 4.0~), python3-bibtexparser (=1.2~), python3-feedparser (=6.0~), python3-pillow (=9.0~)" >> build/package/DEBIAN/control
	$(Q)echo "Recommends: systemd" >> build/package/DEBIAN/control
	$(Q)echo "Installed-Size: `du -sk build/package/usr | grep -oE "[0-9]+"`" >> build/package/DEBIAN/control
	$(Q)echo "Maintainer: J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>" >> build/package/DEBIAN/control
	$(Q)echo "Homepage: https://github.com/jnphilipp/bibliothek" >> build/package/DEBIAN/control
	$(Q)echo "Description: Library managing tool for the command line" >> build/package/DEBIAN/control
	$(Q)echo " This tool provides a command line interfaces to manage books with different" >> build/package/DEBIAN/control
	$(Q)echo " editions, magazines or scientific papers." >> build/package/DEBIAN/control
	$(Q)echo " It includes a search provider for the GNOME desktop." >> build/package/DEBIAN/control
	$(Q)echo " It has also a web interface that can be run as a systemd service." >> build/package/DEBIAN/control
