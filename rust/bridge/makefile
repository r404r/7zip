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

!include "../../CPP/7zip/Bundles/Format7zF/Arc.mak"

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

!include "../../CPP/7zip/7zip.mak"

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

# The corresponding explicit per-object recipes are deliberately represented
# as source/object pairs so the NMAKE qualifying card can retain every existing
# COMPLB option and append only this one definition. The guard above prevents
# this declaration from producing an unqualified Windows binary today.
REGISTER_ARC_CPP = \
  ../../Archive/ApfsHandler.cpp ../../Archive/ApmHandler.cpp ../../Archive/ArHandler.cpp ../../Archive/ArjHandler.cpp \
  ../../Archive/Base64Handler.cpp ../../Archive/Bz2Handler.cpp ../../Archive/ComHandler.cpp ../../Archive/CpioHandler.cpp \
  ../../Archive/CramfsHandler.cpp ../../Archive/DmgHandler.cpp ../../Archive/ElfHandler.cpp ../../Archive/ExtHandler.cpp \
  ../../Archive/FatHandler.cpp ../../Archive/FlvHandler.cpp ../../Archive/GptHandler.cpp ../../Archive/GzHandler.cpp \
  ../../Archive/HfsHandler.cpp ../../Archive/IhexHandler.cpp ../../Archive/LpHandler.cpp ../../Archive/LzhHandler.cpp \
  ../../Archive/LzmaHandler.cpp ../../Archive/MachoHandler.cpp ../../Archive/MbrHandler.cpp ../../Archive/MslzHandler.cpp \
  ../../Archive/MubHandler.cpp ../../Archive/NtfsHandler.cpp ../../Archive/PeHandler.cpp ../../Archive/PpmdHandler.cpp \
  ../../Archive/QcowHandler.cpp ../../Archive/RpmHandler.cpp ../../Archive/SparseHandler.cpp ../../Archive/SplitHandler.cpp \
  ../../Archive/SquashfsHandler.cpp ../../Archive/SwfHandler.cpp ../../Archive/UefiHandler.cpp ../../Archive/VdiHandler.cpp \
  ../../Archive/VhdHandler.cpp ../../Archive/VhdxHandler.cpp ../../Archive/VmdkHandler.cpp ../../Archive/XarHandler.cpp \
  ../../Archive/XzHandler.cpp ../../Archive/ZHandler.cpp ../../Archive/ZstdHandler.cpp ../../Archive/7z/7zRegister.cpp \
  ../../Archive/Cab/CabRegister.cpp ../../Archive/Chm/ChmHandler.cpp ../../Archive/Iso/IsoRegister.cpp ../../Archive/Nsis/NsisRegister.cpp \
  ../../Archive/Rar/RarHandler.cpp ../../Archive/Rar/Rar5Handler.cpp ../../Archive/Tar/TarRegister.cpp ../../Archive/Udf/UdfHandler.cpp \
  ../../Archive/Wim/WimRegister.cpp ../../Archive/Zip/ZipRegister.cpp

# Qualification-only recipe template: each member of REGISTER_ARC_OBJS must use
# its paired REGISTER_ARC_CPP source and this exact additional definition.
# $(COMPLB) /DRegisterArc=ArchiveBridgeRegisterArc
