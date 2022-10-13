.DEFAULT_GOAL := help

ESP_DEVICE ?= /dev/ttyUSB0
ESP_BAUD_RATE := 460800
ESPTOOL_ARGS := --port "$(ESP_DEVICE)" --baud "$(ESP_BAUD_RATE)"

RSHELL_BOARD_PATH := /pyboard
RSHELL_BAUD_RATE := 115200
RSHELL_ARGS := --port "$(ESP_DEVICE)" --baud "$(RSHELL_BAUD_RATE)"

MICROPYTHON_VERSION := v1.19.1
MICROPYTHON_RELEASE := esp8266-20220618-$(MICROPYTHON_VERSION).bin
MICROPYTHON_FIRMWARE_URL := https://micropython.org/resources/firmware/$(MICROPYTHON_RELEASE)
MICROPYTHON_REPO_URL := https://github.com/micropython/micropython.git

VENDOR_DIR := dist/vendor


all: push


dist: toolchain  ## Compile the app into a distributable bundle
	cp -rp src dist
	if [ -d "$(VENDOR_DIR)" ]; then \
        find "$(VENDOR_DIR)" -type f -name "*.py" -exec toolchain/mpy-cross {} \; -exec rm -f {} \; ; \
    fi


toolchain: toolchain/mpy-cross toolchain/$(MICROPYTHON_RELEASE)  ## Setup build tools


toolchain/mpy-cross: private TEMP_DIR := "$(shell mktemp -d)"
toolchain/mpy-cross:
	git clone "$(MICROPYTHON_REPO_URL)" "$(TEMP_DIR)"
	cd "$(TEMP_DIR)/mpy-cross" \
		&& git checkout "$(MICROPYTHON_VERSION)" \
		&& make

	mkdir -p toolchain
	cp "$(TEMP_DIR)/mpy-cross/mpy-cross" ./toolchain

	rm -rf "$(TEMP_DIR)"


toolchain/$(MICROPYTHON_RELEASE):
	wget -O "toolchain/$(MICROPYTHON_RELEASE)" "$(MICROPYTHON_FIRMWARE_URL)"


.PHONY: dialout
dialout:  ## Validates the user can interact with the esp board via the serial port
	@echo "Validating user is in the dialout group"
	test "$(shell id --user)" = "0" || (id --name --groups | grep --quiet --word-regexp "dialout")
	@echo "Ok"


.PHONY: flash-board
flash-board: dialout toolchain  ## Write MicroPython firmware into the esp board, only needed once
	poetry run esptool.py $(ESPTOOL_ARGS) erase_flash
	poetry run esptool.py $(ESPTOOL_ARGS) write_flash \
		--flash_size=detect 0 "toolchain/$(MICROPYTHON_RELEASE)"


.PHONY: push
push: dialout dist  ## Push bundled application to the esp board
	poetry run rshell $(RSHELL_ARGS) rsync \
		--all --mirror dist/ $(RSHELL_BOARD_PATH)


.PHONY: wipe
wipe: clean  ## Remove all generated artifacts in this repository
	rm -rf toolchain


.PHONY: clean
clean:  ## Remove the compiled app
	rm -rf dist


.PHONY: help
help:  ## Print this message
	@echo "USAGE"
	@echo "  export ESP_DEVICE=/dev/...  # Points to $(ESP_DEVICE) by default"
	@echo "  make flash-board  # Flash MicroPython firmware, you only have to launch this once"
	@echo "  make all  # Bundle application and push it to the esp board"
	@echo
	@echo "TARGETS"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'
