SHELL=/bin/bash
.DEFAULT_GOAL := help
.SUFFIXES:

BOARD_SERIAL_DEVICE ?= /dev/ttyUSB0
BOARD_BAUD_RATE := 460800
ESPTOOL_CMD := esptool.py --port "$(BOARD_SERIAL_DEVICE)" --baud "$(BOARD_BAUD_RATE)"

RSHELL_BOARD_PATH := /pyboard
RSHELL_BAUD_RATE := 115200
RSHELL_CMD := rshell --port "$(BOARD_SERIAL_DEVICE)" --baud "$(RSHELL_BAUD_RATE)"

MICROPYTHON_REPO_URL := https://github.com/micropython/micropython.git
MICROPYTHON_VERSION := v1.19.1
MICROPYTHON_TARGET_PORT := esp8266
MICROPYTHON_TARGET_BOARD := GENERIC
MICROPYTHON_TARGET_DIR := micropython/ports/$(MICROPYTHON_TARGET_PORT)
MICROPYTHON_FROZEN_LIB_DIR := $(MICROPYTHON_TARGET_DIR)/modules
MICROPYTHON_FIRMWARE := toolchain/$(MICROPYTHON_TARGET_DIR)/build-$(MICROPYTHON_TARGET_BOARD)/firmware-combined.bin
MPYCROSS_BIN := toolchain/micropython/mpy-cross/mpy-cross

SDK_DOCKER_REPOSITORY := larsks/esp-open-sdk:latest
SDK_DOCKER_CMD := docker run --rm -v "$$PWD/toolchain:/opt" -u "$$UID" -w "/opt" "$(SDK_DOCKER_REPOSITORY)"
SERIAL_DOCKER_IMAGE_SLUG := micropython_serial_tools:d0f6fc28f8bc
SERIAL_DOCKER_CMD := docker run --rm -it -v "$$PWD:/opt" -w "/opt" --device=$(BOARD_SERIAL_DEVICE) "$(SERIAL_DOCKER_IMAGE_SLUG)"

SOURCE_FILES := $(shell find src -type f)
FROZEN_FILES := $(shell find frozen -type f)

WIFI_CREDENTIALS_FILE := etc/wifi.secret.json


toolchain/micropython:
	mkdir -p toolchain
	git clone --branch "$(MICROPYTHON_VERSION)" "$(MICROPYTHON_REPO_URL)" toolchain/micropython

$(MPYCROSS_BIN): toolchain/micropython
	$(SDK_DOCKER_CMD) make -C micropython/mpy-cross

$(MICROPYTHON_FIRMWARE): $(MPYCROSS_BIN) $(FROZEN_FILES)
	cd "toolchain/$(MICROPYTHON_FROZEN_LIB_DIR)" && git clean -dxf
	cp -rp frozen/* "toolchain/$(MICROPYTHON_FROZEN_LIB_DIR)"
	$(SDK_DOCKER_CMD) make -j -C "$(MICROPYTHON_TARGET_DIR)" submodules
	$(SDK_DOCKER_CMD) make -j -C "$(MICROPYTHON_TARGET_DIR)" \
		"BOARD=$(MICROPYTHON_TARGET_BOARD)" all


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

build: $(SOURCE_FILES) $(MICROPYTHON_FIRMWARE)  ## Compile the app and firmware
	rm -rf build
	mkdir -p build

	cp -p $(MICROPYTHON_FIRMWARE) build/firmware.bin
	cp -rp src build/app

	cd build && find * -type f -name "*.py" \
		-exec bash -c "$$compile_mpy_script" find_exec_snippet {} \; ; \


.PHONY: docker
docker:
	@docker image inspect "$(SERIAL_DOCKER_IMAGE_SLUG)" &> /dev/null || ( \
		echo "Building docker image $(SERIAL_DOCKER_IMAGE_SLUG)"; \
		docker build -t "$(SERIAL_DOCKER_IMAGE_SLUG)" docker \
	)


.PHONY: flash
flash: docker build  ## Write MicroPython firmware into the esp board
	$(SERIAL_DOCKER_CMD) $(ESPTOOL_CMD) erase_flash
	$(SERIAL_DOCKER_CMD) $(ESPTOOL_CMD) write_flash \
		--flash_size=detect 0 "build/firmware.bin"


.PHONY: push
push: docker build etc skel  ## Push precompiled application to the esp board and restart
	$(SERIAL_DOCKER_CMD) $(RSHELL_CMD) rsync \
		--all skel/ "$(RSHELL_BOARD_PATH)"

	$(SERIAL_DOCKER_CMD) $(RSHELL_CMD) rsync \
		--all --mirror etc/ "$(RSHELL_BOARD_PATH)/etc"

	$(SERIAL_DOCKER_CMD) $(RSHELL_CMD) rsync \
		--all --mirror build/app/ "$(RSHELL_BOARD_PATH)/app"


.PHONY: setup-wifi
setup-wifi:  ## Setup wifi credentials
	@if [[ -f "$(WIFI_CREDENTIALS_FILE)" ]]; then \
		echo "Wifi cretentials found: $(WIFI_CREDENTIALS_FILE)"; \
	else \
		echo "Configuring wifi credentials..."; \
		read -p "SSID (wifi network name): " ssid; \
		read -sp "Password: " pass; \
		echo -e "{\n    \"ssid\": \"$$ssid\",\n    \"key\": \"$$pass\"\n}" > "$(WIFI_CREDENTIALS_FILE)"; \
		echo -e "\nWifi credentials configured: $(WIFI_CREDENTIALS_FILE)"; \
	fi


.PHONY: show-ip
show-ip:  ## Show the IP address of the board
	@sleep 2  # Wait a bit to give the board a chance to setup the wlan config
	$(SERIAL_DOCKER_CMD) $(RSHELL_CMD) repl "~ import utils ~ utils.show_ip() ~ utils.reset(soft=True) ~"


.PHONY: all
all: setup-wifi flash push restart  ## Same as: make setup-wifi flash push restart

.PHONY: attach
attach: docker  ## Attach to the Python interpreter and start the application
	$(SERIAL_DOCKER_CMD) $(RSHELL_CMD) repl '~ import main'


.PHONY: reset
reset: docker  ## Restart the board
	$(SERIAL_DOCKER_CMD) $(RSHELL_CMD) repl '~ import utils ~ utils.reset() ~'


.PHONY: rshell
rshell: docker  ## Open rshell
	exec $(SERIAL_DOCKER_CMD) $(RSHELL_CMD)


.PHONY: repl
repl: docker  ## Open a Python interpreter in the esp board
	exec $(SERIAL_DOCKER_CMD) $(RSHELL_CMD) repl


.PHONY: toolchain
toolchain: $(MPYCROSS_BIN)  ## Setup the tools for building the MicroPython firmware


.PHONY: compile
compile: $(MPYCROSS_BIN) $(MICROPYTHON_FIRMWARE)   ## Compile the MicroPython firmware


.PHONY: clean
clean:  ## Remove the compiled firmware and app
	rm -rf build
	cd "toolchain/$(MICROPYTHON_TARGET_DIR)" && git clean -dxf || true


.PHONY: wipe
wipe:  ## Remove all generated artifacts
	rm -rf build toolchain


.PHONY: help
help:  ## Print this message
	@echo "USAGE"
	@echo "  export BOARD_SERIAL_DEVICE=/dev/...  # Points to $(BOARD_SERIAL_DEVICE) by default"
	@echo "  make flash-board  # Flash MicroPython firmware, just needed once"
	@echo "  make all  # Bundle application and push it to the esp board"
	@echo
	@echo "TARGETS"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'
