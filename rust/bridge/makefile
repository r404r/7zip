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
# Two Windows-specific problems the qualifying card must solve, neither of
# which this development slice claims to have solved:
#
# 1. Registration-byte recovery. CArcInfoEx drops CArcInfo::Id, so
#    rust/bridge/archive_bridge_v1.cpp recovers it by wrapping the retained
#    registrar at link time with GNU ld's --wrap, keyed on the Itanium C++ ABI
#    mangling of RegisterArc(const CArcInfo *). MSVC's link.exe has no --wrap
#    and a different mangling, so Windows needs its own reviewed mechanism.
#
# 2. Calling convention. Per docs/ai-migration/qualification/abi-v1.md every
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

!include "../../CPP/7zip/7zip.mak"
