SHELL=/bin/bash
.DEFAULT_GOAL := help

BOARD_SERIAL_DEVICE ?= /dev/ttyUSB0
BOARD_BAUD_RATE := 460800
ESPTOOL_ARGS := --port "$(BOARD_SERIAL_DEVICE)" --baud "$(BOARD_BAUD_RATE)"

RSHELL_BOARD_PATH := /pyboard
RSHELL_BAUD_RATE := 115200
RSHELL_ARGS := --port "$(BOARD_SERIAL_DEVICE)" --baud "$(RSHELL_BAUD_RATE)"

MICROPYTHON_VERSION := v1.19.1
MICROPYTHON_TARGET_PORT := esp8266
MICROPYTHON_TARGET_BOARD := GENERIC
MICROPYTHON_REPO_URL := https://github.com/micropython/micropython.git
MPYCROSS_BIN := toolchain/micropython/mpy-cross/mpy-cross
XCOMPILER_PATH := xcompiler/xtensa-lx106-elf/bin

ESP_IDF_VERSION := v4.4.2
ESP_IDF_TARGET := esp32
ESP_IDF_REPO := https://github.com/espressif/esp-idf.git

DOCKER_ESP_SLUG := esptoolchain:latest
DOCKER_READY_FILE := .docker_image_built.ignore

USER := $(shell id -nu)
UID := $(shell id -u)
GID := $(shell id -g)
SOURCE_FILES := $(shell find src -type f)


# This snippet transforms a .py file into an .mpy file, while preserving timestamps
define compile_mpy_script
	src_file="$$1"
	final_path="/$$src_file"
	dst_file="$${src_file%.py}.mpy"

	"../$(MPYCROSS_BIN)" -s "$$final_path" -o "$$dst_file" "$$src_file"
	touch -r "$$src_file" "$$dst_file"

	rm -f "$$src_file"
endef
export compile_mpy_script

dist: toolchain $(SOURCE_FILES)  ## Compile the app into a distributable bundle
	rm -rf dist
	mkdir dist

	cp -rp src dist/app

	cd dist && find * -type f -name "*.py" \
		-exec bash -c "$$compile_mpy_script" find_exec_snippet {} \; ; \


.PHONY: docker
docker: $(DOCKER_READY_FILE)  ## Build necessary docker images

$(DOCKER_READY_FILE):
	docker images -q "$(DOCKER_ESP_SLUG)" && exit 0

	docker build \
		-t "$(DOCKER_ESP_SLUG)" \
		--build-arg USER="$(USER)" \
		--build-arg UID="$(UID)" \
		--build-arg GID="$(GID)" \
		.

	touch $(DOCKER_READY_FILE)

toolchain:  toolchain/esp-idf toolchain/micropython  ## Setup the tools for building the MicroPython firmware
	poetry install

toolchain/esp-idf:
	mkdir -p toolchain
	git clone --recursive --branch "$(ESP_IDF_VERSION)" "$(ESP_IDF_REPO)" toolchain/esp-idf

toolchain/micropython:
	mkdir -p toolchain
	git clone --branch "$(MICROPYTHON_VERSION)" "$(MICROPYTHON_REPO_URL)" toolchain/micropython


$(MPYCROSS_BIN): toolchain $(DOCKER_READY_FILE)
	docker run --rm -it -v "$$PWD/toolchain:/opt" "$(DOCKER_ESP_SLUG)" \
		make -C micropython/mpy-cross


toolchain/expressif: toolchain $(DOCKER_READY_FILE)
	mkdir -p toolchain/expressif
	docker run --rm -it -v "$$PWD/toolchain:/opt" -e IDF_TOOLS_PATH="/opt/expressif" \
		"$(DOCKER_ESP_SLUG)" \
		bash -c 'cd esp-idf; ./install.sh "$(ESP_IDF_TARGET)"'


$(XCOMPILER_PATH): toolchain $(DOCKER_READY_FILE)
	mkdir -p toolchain/xcompiler
	docker run --rm -it -v "$$PWD/toolchain:/opt" \
		"$(DOCKER_ESP_SLUG)" \
		bash -c 'cd xcompiler; source ../micropython/tools/ci.sh && ci_esp8266_setup; \
			echo touch "/opt/$(XCOMPILER_PATH)"'


#build: toolchain/expressif $(MPYCROSS_BIN) frozenlib  ## Build the MicroPython firmware
#	docker run --rm -it -v "$$PWD/toolchain:/opt" \
#		-e IDF_TOOLS_PATH="/opt/expressif" -e BOARD="$(MICROPYTHON_TARGET_BOARD)" \
#		"$(DOCKER_ESP_SLUG)" \
#		bash -c 'cd esp-idf; source ./export.sh; \
#			cd ../micropython/ports/$(MICROPYTHON_TARGET_PORT); \
#			make submodules && make'


build: $(XCOMPILER_PATH) $(MPYCROSS_BIN) $(DOCKER_READY_FILE) frozenlib  ## Build the MicroPython firmware
	docker run --rm -it -v "$$PWD/toolchain:/opt" \
		-e IDF_PATH="/opt/esp-idf" -e ESPIDF="/opt/esp-idf" \
		-e BOARD="$(MICROPYTHON_TARGET_BOARD)" \
		"$(DOCKER_ESP_SLUG)" \
		bash -c 'export PATH="/opt/$(XCOMPILER_PATH):$$PATH"; \
			cd "micropython/ports/$(MICROPYTHON_TARGET_PORT)"; \
			make submodules && make'


.PHONY: dialout
dialout:  ## Validates the user can interact with the esp board via the serial port
	@echo "Validating user is in the dialout group"
	test "$(shell id --user)" = "0" || (id --name --groups | grep --quiet --word-regexp "dialout")
	@echo "Ok"


.PHONY: flash-board
flash-board: dialout toolchain build  ## Write MicroPython firmware into the esp board, only needed once
	poetry run esptool.py $(ESPTOOL_ARGS) erase_flash
	poetry run esptool.py $(ESPTOOL_ARGS) write_flash \
		--flash_size=detect 0 "toolchain/$(MICROPYTHON_RELEASE)"


.PHONY: push
push: dialout toolchain dist config skel  ## Push bundled application to the esp board and restart
	poetry run rshell $(RSHELL_ARGS) rsync \
		--all skel/ "$(RSHELL_BOARD_PATH)"

	poetry run rshell $(RSHELL_ARGS) rsync \
		--all --mirror config/ "$(RSHELL_BOARD_PATH)/config"

	poetry run rshell $(RSHELL_ARGS) rsync \
		--all --mirror dist/app/ "$(RSHELL_BOARD_PATH)/app"


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
	rm -rf build toolchain


.PHONY: clean
clean:  ## Remove the compiled app
	rm -rf dist


.PHONY: help
help:  ## Print this message
	@echo "USAGE"
	@echo "  export BOARD_SERIAL_DEVICE=/dev/...  # Points to $(BOARD_SERIAL_DEVICE) by default"
	@echo "  make flash-board  # Flash MicroPython firmware, just needed once"
	@echo "  make all  # Bundle application and push it to the esp board"
	@echo
	@echo "TARGETS"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'
