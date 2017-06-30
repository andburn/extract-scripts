MAKEFILE := $(lastword $(MAKEFILE_LIST))
BASE_DIR := .
BUILD_DIR := $(BASE_DIR)/build
MSBUILD_BIN := msbuild
LIBS := Mono.Cecil.dll ICSharpCode.Decompiler.dll ICSharpCode.NRefactory.dll ICSharpCode.NRefactory.CSharp.dll

SOURCES := decompile.cs

.SUFFIXES: .cs .exe
.PHONY: all clean depends


all: decompile.exe


depends:
	$(eval csproj := ILSpy/ICSharpCode.Decompiler/ICSharpCode.Decompiler.csproj)
	$(MSBUILD_BIN) $(csproj)
	$(MSBUILD_BIN) /property:OutputPath=$(BUILD_DIR) $(csproj)

decompile.exe: depends
	cp $(foreach lib,$(LIBS),ILSpy/ICSharpCode.Decompiler/$(BUILD_DIR)/$(lib)) $(BUILD_DIR)
	$(eval flags := $(foreach lib,$(LIBS),-r:$(BUILD_DIR)/$(lib)))
	mcs -debug -out:$(BUILD_DIR)/$(patsubst %.cs,%.exe,$@) $(flags) $(SOURCES)

clean:
	test -d $(BUILD_DIR) && rm -rf $(BUILD_DIR)
