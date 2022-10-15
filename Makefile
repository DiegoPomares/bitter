SHELL=/bin/bash
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

SOURCE_FILES := $(shell find lib src -type f)


# This snippet transforms a .py file into an .mpy file, while preserving timestamps
define compile_mpy_script
	src_file="$$1"
	final_path="/$$src_file"
	dst_file="$${src_file%.py}.mpy"

	../toolchain/mpy-cross -s "$$final_path" -o "$$dst_file" "$$src_file"
	touch -r "$$src_file" "$$dst_file"

	rm -f "$$src_file"
endef
export compile_mpy_script

dist: toolchain $(SOURCE_FILES)  ## Compile the app into a distributable bundle
	rm -rf dist
	mkdir dist

	cp -rp lib dist
	cp -rp src dist/app

	cd dist && find * -type f -name "*.py" \
		-exec bash -c "$$compile_mpy_script" find_exec_snippet {} \; ; \


toolchain: toolchain/mpy-cross toolchain/$(MICROPYTHON_RELEASE)  ## Setup build tools
	poetry install


toolchain/mpy-cross: private TEMP_DIR := $(shell mktemp -d)
toolchain/mpy-cross:
	git clone "$(MICROPYTHON_REPO_URL)" "$(TEMP_DIR)"
	cd "$(TEMP_DIR)/mpy-cross" \
		&& git checkout "$(MICROPYTHON_VERSION)" \
		&& make

	mkdir -p toolchain
	cp "$(TEMP_DIR)/mpy-cross/mpy-cross" ./toolchain

	rm -rf "$(TEMP_DIR)"


toolchain/$(MICROPYTHON_RELEASE):
	mkdir -p toolchain
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
push: dialout dist config skel  ## Push bundled application to the esp board and restart
	poetry run rshell $(RSHELL_ARGS) rsync \
		--all skel/ "$(RSHELL_BOARD_PATH)"

	poetry run rshell $(RSHELL_ARGS) rsync \
		--all --mirror dist/ "$(RSHELL_BOARD_PATH)/app"

	poetry run rshell $(RSHELL_ARGS) rsync \
		--all --mirror config/ "$(RSHELL_BOARD_PATH)/config"


.PHONY: rshell
rshell: toolchain  ## Open rshell
	exec poetry run rshell $(RSHELL_ARGS)


.PHONY: repl
repl: toolchain  ## Open a Python interpreter in the esp board
	exec poetry run rshell $(RSHELL_ARGS) repl


.PHONY: reset
reset: toolchain  ## Restart the board
	poetry run rshell $(RSHELL_ARGS) repl '~ import machine ~ machine.reset() ~'


.PHONY: attach
attach: toolchain  ## Attach to the Python interpreter and start the application
	poetry run rshell $(RSHELL_ARGS) repl '~ exec(open("main.py").read())'


.PHONY: wipe
wipe: clean  ## Remove all generated artifacts in this repository
	rm -rf toolchain


.PHONY: clean
clean:  ## Remove the compiled app
	rm -rf dist


.PHONY: vscode
vscode: .vscode  ## Setup stubs for VSCode IntelliSense

.vscode: private TEMP_DIR := $(shell mktemp -d)
.vscode: private PROJECT_NAME := $(shell basename "$(PWD)")
.vscode:
	poetry run micropy stubs add "$(MICROPYTHON_STUBS)"
	poetry run micropy init --template vscode --name "$(PROJECT_NAME)" "$(TEMP_DIR)"
	cd "$(TEMP_DIR)" \
		&& ls -la

	mv "$(TEMP_DIR)/"{.vscode,.micropy} .
	rm -rf "$(TEMP_DIR)"


.PHONY: help
help:  ## Print this message
	@echo "USAGE"
	@echo "  export ESP_DEVICE=/dev/...  # Points to $(ESP_DEVICE) by default"
	@echo "  make flash-board  # Flash MicroPython firmware, just needed once"
	@echo "  make all  # Bundle application and push it to the esp board"
	@echo
	@echo "TARGETS"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'
