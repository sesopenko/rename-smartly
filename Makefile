DEB_NAME=rename-smartly
VERSION ?= 1.0
DEB_DIR=$(DEB_NAME)_$(VERSION)
PY_SRC=rename_smartly/main.py
PY_DST=$(DEB_DIR)/usr/lib/rename-smartly/main.py
DEB_FILE=$(DEB_NAME)_$(VERSION)_all.deb

.PHONY: prepare-deb build-deb clean

prepare-deb:
	@echo "Preparing Debian package directory for version $(VERSION)..."
	mkdir -p $(DEB_DIR)/usr/lib/rename-smartly
	mkdir -p $(DEB_DIR)/usr/bin
	mkdir -p $(DEB_DIR)/usr/share/applications
	mkdir -p $(DEB_DIR)/usr/share/doc/rename-smartly
	mkdir -p $(DEB_DIR)/DEBIAN

	cp $(PY_SRC) $(PY_DST)
	cp deb/usr/bin/rename-smartly $(DEB_DIR)/usr/bin/
	chmod +x $(DEB_DIR)/usr/bin/rename-smartly

	cp deb/usr/share/doc/rename-smartly/* $(DEB_DIR)/usr/share/doc/rename-smartly/
	chmod +x $(DEB_DIR)/usr/share/doc/rename-smartly/nautilus-script

	cp deb/usr/share/applications/rename-smartly.desktop $(DEB_DIR)/usr/share/applications/
	chmod 644 $(DEB_DIR)/usr/share/applications/rename-smartly.desktop

	# Generate control file from template
	sed "s/@VERSION@/$(VERSION)/" deb/DEBIAN/control.in > $(DEB_DIR)/DEBIAN/control

	# Copy other DEBIAN scripts
	cp deb/DEBIAN/postrm $(DEB_DIR)/DEBIAN/
	chmod +x $(DEB_DIR)/DEBIAN/postrm

	echo "Copied $(PY_SRC) to $(PY_DST)"

build-deb: prepare-deb
	@echo "Building .deb package..."
	dpkg-deb --build $(DEB_DIR)
	mv $(DEB_DIR).deb $(DEB_FILE)
	@echo "Created $(DEB_FILE)"

clean:
	@echo "Cleaning up..."
	rm -rf $(DEB_DIR)
	rm -f $(DEB_FILE)
