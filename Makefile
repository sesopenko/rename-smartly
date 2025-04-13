DEB_NAME=rename-smartly
DEB_VERSION=1.0
DEB_DIR=$(DEB_NAME)_$(DEB_VERSION)
PY_SRC=rename_smartly/main.py
PY_DST=$(DEB_DIR)/usr/lib/rename-smartly/main.py
DEB_FILE=$(DEB_DIR).deb

.PHONY: prepare-deb build-deb clean

prepare-deb:
	@echo "Preparing Debian package directory..."
	mkdir -p $(DEB_DIR)/usr/lib/rename-smartly
	mkdir -p $(DEB_DIR)/usr/bin
	mkdir -p $(DEB_DIR)/usr/share/application
	mkdir -p $(DEB_DIR)/DEBIAN
	cp $(PY_SRC) $(PY_DST)
	cp deb/usr/bin/rename-smartly $(DEB_DIR)/usr/bin/
	chmod +x $(DEB_DIR)/usr/bin/rename-smartly
	cp deb/DEBIAN/control $(DEB_DIR)/DEBIAN/
	cp deb/usr/share/application/rename-smartly.desktop $(DEB_DIR)/usr/share/application/
	echo "Copied $(PY_SRC) to $(PY_DST)"

build-deb: prepare-deb
	@echo "Building .deb package..."
	dpkg-deb --build $(DEB_DIR)
	echo "Created $(DEB_FILE)"

clean:
	@echo "Cleaning up..."
	rm -rf $(DEB_DIR)
