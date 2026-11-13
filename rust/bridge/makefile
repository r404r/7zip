# S2a-DEV facade build, MSVC nmake variant. DECLARATION ONLY, NOT QUALIFIED.
#
# Read this first: no Windows facade build has been performed. S2a-DEV is a
# single-host Linux development build (see
# docs/ai-migration/qualification/s2a-dev.md). Native Windows, macOS and Linux
# facade qualification — matched builds, ABI widths, calling convention,
# sanitizers and dead-strip retention — is a deferred obligation on S2a
# t_071e4cd7 and is NOT satisfied by this file.
#
# This makefile therefore fails closed. It records the retained inputs a
# Windows facade build must use, in the same shape as
# CPP/7zip/Bundles/Format7zF/makefile, and refuses to run until that card
# actually qualifies it. An unqualified Windows binary must not be producible
# by accident.
#
# The Windows qualification card must verify the per-object preprocessor
# redirection used by the portable shim and must also solve this independent
# calling-convention issue. Per docs/ai-migration/qualification/abi-v1.md every
#    exported and callback function must use __cdecl explicitly, overriding the
#    retained engine's -Gr default set in CPP/Build.mak:53. The header's
#    ARCHIVE_BRIDGE_V1_CALL macro already spells that; it must be verified
#    against real MSVC output, not assumed.

!ERROR S2a-DEV performs no Windows facade build. Native Windows facade \
qualification is a deferred obligation on S2a t_071e4cd7; see \
docs/ai-migration/qualification/s2a-dev.md. This makefile is a declaration of \
the retained inputs, not an authorized build.

# Below this point nothing executes. It is retained as the reviewed starting
# shape for the qualifying card, mirroring the retained Format7zF makefile.

PROG = archive_bridge_v1.dll

# Z7_EXTERNAL_CODECS is deliberately NOT defined: the frozen Q1 identity pins
# plugin_policy to built-in-only-no-external-discovery, so CCodecs uses only
# its built-in registration tables and loads no external module.
CFLAGS = $(CFLAGS)

!include "Arc.mak"

# Only the two UI_COMMON_OBJS members that supply the retained capability
# tables: LoadCodecs.obj for CCodecs/CArcInfoEx and HashCalc.obj for
# Codecs_AddHashArcHandler. No console object is linked.
UI_COMMON_OBJS = \
  $O\HashCalc.obj \
  $O\LoadCodecs.obj \

# Retained objects the two members above reference. These add link closure,
# not new capabilities.
UI_COMMON_OBJS = $(UI_COMMON_OBJS) \
  $O\EnumDirItems.obj \
  $O\SortUtils.obj \

WIN_OBJS = $(WIN_OBJS) \
  $O\ErrorMsg.obj \
  $O\FileLink.obj \

7ZIP_COMMON_OBJS = $(7ZIP_COMMON_OBJS) \
  $O\FileStreams.obj \

CURRENT_OBJS = \
  $O\archive_bridge_v1.obj \
  $O\archive_bridge_registration.obj \
  $O\archive_bridge_registration_correspondence.obj \

!include "../../7zip.mak"

# Bridge-owned translation units are outside the retained inference-rule tree.
# Compile them explicitly without the RegisterArc redirection and without the
# retained StdAfx precompiled header.
$O\archive_bridge_v1.obj: ../../../../rust/bridge/archive_bridge_v1.cpp
	$(COMPLB_O2) /I"../../../../"
$O\archive_bridge_registration.obj: ../../../../rust/bridge/archive_bridge_registration.cpp
	$(COMPLB_O2) /I"../../../../"
$O\archive_bridge_registration_correspondence.obj: ../../../../rust/bridge/archive_bridge_registration_correspondence.cpp
	$(COMPLB_O2) /I"../../../../"

# Kept below the fail-closed guard as a declaration for the future qualifying
# card. This list is intentionally explicit and must match makefile.gcc by
# basename; it is never a global CFLAGS addition.
REGISTER_ARC_OBJS = \
  $O\ApfsHandler.obj $O\ApmHandler.obj $O\ArHandler.obj $O\ArjHandler.obj \
  $O\Base64Handler.obj $O\Bz2Handler.obj $O\ComHandler.obj $O\CpioHandler.obj \
  $O\CramfsHandler.obj $O\DmgHandler.obj $O\ElfHandler.obj $O\ExtHandler.obj \
  $O\FatHandler.obj $O\FlvHandler.obj $O\GptHandler.obj $O\GzHandler.obj \
  $O\HfsHandler.obj $O\IhexHandler.obj $O\LpHandler.obj $O\LzhHandler.obj \
  $O\LzmaHandler.obj $O\MachoHandler.obj $O\MbrHandler.obj $O\MslzHandler.obj \
  $O\MubHandler.obj $O\NtfsHandler.obj $O\PeHandler.obj $O\PpmdHandler.obj \
  $O\QcowHandler.obj $O\RpmHandler.obj $O\SparseHandler.obj $O\SplitHandler.obj \
  $O\SquashfsHandler.obj $O\SwfHandler.obj $O\UefiHandler.obj $O\VdiHandler.obj \
  $O\VhdHandler.obj $O\VhdxHandler.obj $O\VmdkHandler.obj $O\XarHandler.obj \
  $O\XzHandler.obj $O\ZHandler.obj $O\ZstdHandler.obj $O\7zRegister.obj \
  $O\CabRegister.obj $O\ChmHandler.obj $O\IsoRegister.obj $O\NsisRegister.obj \
  $O\RarHandler.obj $O\Rar5Handler.obj $O\TarRegister.obj $O\UdfHandler.obj \
  $O\WimRegister.obj $O\ZipRegister.obj

# These explicit recipes take precedence over the retained inference rules and
# append the redirection only to the selected registration translation units.
$O\ApfsHandler.obj: ../../Archive/ApfsHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ApmHandler.obj: ../../Archive/ApmHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ArHandler.obj: ../../Archive/ArHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ArjHandler.obj: ../../Archive/ArjHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\Base64Handler.obj: ../../Archive/Base64Handler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\Bz2Handler.obj: ../../Archive/Bz2Handler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ComHandler.obj: ../../Archive/ComHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\CpioHandler.obj: ../../Archive/CpioHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\CramfsHandler.obj: ../../Archive/CramfsHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\DmgHandler.obj: ../../Archive/DmgHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ElfHandler.obj: ../../Archive/ElfHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ExtHandler.obj: ../../Archive/ExtHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\FatHandler.obj: ../../Archive/FatHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\FlvHandler.obj: ../../Archive/FlvHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\GptHandler.obj: ../../Archive/GptHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\GzHandler.obj: ../../Archive/GzHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\HfsHandler.obj: ../../Archive/HfsHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\IhexHandler.obj: ../../Archive/IhexHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\LpHandler.obj: ../../Archive/LpHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\LzhHandler.obj: ../../Archive/LzhHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\LzmaHandler.obj: ../../Archive/LzmaHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\MachoHandler.obj: ../../Archive/MachoHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\MbrHandler.obj: ../../Archive/MbrHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\MslzHandler.obj: ../../Archive/MslzHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\MubHandler.obj: ../../Archive/MubHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\NtfsHandler.obj: ../../Archive/NtfsHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\PeHandler.obj: ../../Archive/PeHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\PpmdHandler.obj: ../../Archive/PpmdHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\QcowHandler.obj: ../../Archive/QcowHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\RpmHandler.obj: ../../Archive/RpmHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\SparseHandler.obj: ../../Archive/SparseHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\SplitHandler.obj: ../../Archive/SplitHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\SquashfsHandler.obj: ../../Archive/SquashfsHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\SwfHandler.obj: ../../Archive/SwfHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\UefiHandler.obj: ../../Archive/UefiHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\VdiHandler.obj: ../../Archive/VdiHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\VhdHandler.obj: ../../Archive/VhdHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\VhdxHandler.obj: ../../Archive/VhdxHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\VmdkHandler.obj: ../../Archive/VmdkHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\XarHandler.obj: ../../Archive/XarHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\XzHandler.obj: ../../Archive/XzHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ZHandler.obj: ../../Archive/ZHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ZstdHandler.obj: ../../Archive/ZstdHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\7zRegister.obj: ../../Archive/7z/7zRegister.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\CabRegister.obj: ../../Archive/Cab/CabRegister.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ChmHandler.obj: ../../Archive/Chm/ChmHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\IsoRegister.obj: ../../Archive/Iso/IsoRegister.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\NsisRegister.obj: ../../Archive/Nsis/NsisRegister.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\RarHandler.obj: ../../Archive/Rar/RarHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\Rar5Handler.obj: ../../Archive/Rar/Rar5Handler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\TarRegister.obj: ../../Archive/Tar/TarRegister.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\UdfHandler.obj: ../../Archive/Udf/UdfHandler.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\WimRegister.obj: ../../Archive/Wim/WimRegister.cpp
	$(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
$O\ZipRegister.obj: ../../Archive/Zip/ZipRegister.cpp
	$(COMPLB) $(ZIP_FLAGS) /DRegisterArc=ArchiveBridgeRegisterArc
