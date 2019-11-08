SHELL := /bin/bash

BASH_COMPLETION_DIR?=/etc/bash_completion.d/
BIN_DIR?=/usr/bin/
DATA_DIR?=/usr/share/
LIB_DIR?=/usr/lib/
SHARE_DIR?=/usr/share/
ICON_DIR?=/usr/share/icons/

FILES := $(shell find bibliothek/* -type f ! -path "**/__pycache__/*" ! -path "**/.git" ! -path "**/.gitignore")


ifdef VERBOSE
  Q :=
else
  Q := @
endif


install: bibliothek.bash-completion build/bin/bibliothek build/bin/gnome-search-provider build/conf/org.gnome.bibliothek.SearchProvider.desktop build/conf/org.gnome.bibliothek.SearchProvider.service.systemd build/conf/org.gnome.bibliothek.SearchProvider.service.dbus build/conf/org.gnome.bibliothek.SearchProvider.ini ${SHARE_DIR}bibliothek/.venv
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


venv:
	$(Q)virtualenv -p /usr/bin/python3 .venv
	$(Q)( \
		source .venv/bin/activate; \
		pip install -r requirements.txt; \
	)
	$(Q)ln -s /usr/lib/python3/dist-packages/gi .venv/lib/python3*/site-packages/
	$(Q)ln -s /usr/lib/python3/dist-packages/dbus .venv/lib/python3*/site-packages/
	$(Q)for f in /usr/lib/python3/dist-packages/_dbus*; do \
		ln -s $$f .venv/lib/python3*/site-packages/; \
	done


${SHARE_DIR}bibliothek:
	mkdir -p ${SHARE_DIR}bibliothek


${SHARE_DIR}bibliothek/.venv:
	$(Q)virtualenv -p /usr/bin/python3 ${SHARE_DIR}bibliothek/.venv
	$(Q)( \
		source ${SHARE_DIR}bibliothek/.venv/bin/activate; \
		pip install -r requirements.txt; \
	)
	$(Q)apt install python3-gi
	$(Q)ln -s /usr/lib/python3/dist-packages/gi ${SHARE_DIR}bibliothek/.venv/lib/python3*/site-packages/
	$(Q)ln -s /usr/lib/python3/dist-packages/dbus ${SHARE_DIR}bibliothek/.venv/lib/python3*/site-packages/
	$(Q)for f in /usr/lib/python3/dist-packages/_dbus*; do \
		ln -s $$f ${SHARE_DIR}bibliothek/.venv/lib/python3*/site-packages/; \
	done

build:
	$(Q)mkdir -p build


build/bin: build
	$(Q)mkdir -p build/bin


build/conf: build
	$(Q)mkdir -p build/conf


build/bin/bibliothek: build/bin
	@echo "#!/usr/bin/env bash" > build/bin/bibliothek
	@echo "cd ${SHARE_DIR}bibliothek" >> build/bin/bibliothek
	@echo ".venv/bin/python3 bibliothek.py \"$$""@\"" >> build/bin/bibliothek


build/bin/gnome-search-provider: build/bin
	@echo "#!/usr/bin/env bash" > build/bin/gnome-search-provider
	@echo "cd ${SHARE_DIR}bibliothek" >> build/bin/gnome-search-provider
	@echo ".venv/bin/python3 gnome-search-provider.py \"$$""@\"" >> build/bin/gnome-search-provider


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


clean:
	$(Q)rm -rf ./build
	$(Q)find bibliothek -name __pycache__ -exec rm -rf {} \;


print-%:
	@echo $*=$($*)
