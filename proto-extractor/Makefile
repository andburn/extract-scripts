MAKEFILE := $(lastword $(MAKEFILE_LIST))
BASE_DIR := $(realpath $(dir $(MAKEFILE)))
BUILD_DIR := $(BASE_DIR)/build
CSPROJ := $(BASE_DIR)/proto-extractor/extractor/extractor.csproj
PKG_FILE := $(BASE_DIR)/proto-extractor/hsproto-packaging.ini

.SUFFIXES: .cs .exe
.PHONY: all clean depends

all: extractor.dll

depends:
	test -d $(BUILD_DIR) || mkdir -p $(BUILD_DIR)
	cp $(PKG_FILE) $(BUILD_DIR)/packaging.ini
	dotnet restore $(CSPROJ)

extractor.dll: depends
	dotnet build --output $(BUILD_DIR) $(CSPROJ)

clean:
	test -d $(BUILD_DIR) && rm -rf $(BUILD_DIR)
