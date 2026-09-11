/* Prerequisite-only bounded probes. All targets are harness-created controls.
   No archive parser, arbitrary command mode, or inherited file descriptors. */
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS
#define _WIN32_WINNT 0x0602
#include <windows.h>
#include <direct.h>
#include <io.h>
#define chdir _chdir
#define chmod _chmod
#else
#define _POSIX_C_SOURCE 200809L
#include <unistd.h>
#endif
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

static FILE *report;
static int write_byte(const char *path)
{
  FILE *f = fopen(path, "wb");
  if (!f) return 0;
  int ok = fputc('X', f) != EOF;
  if (fclose(f) != 0) ok = 0;
  return ok;
}
static int hardlink(const char *target, const char *name)
{
#ifdef _WIN32
  return CreateHardLinkA(name, target, NULL) != 0;
#else
  return link(target, name) == 0;
#endif
}
static int symlink_file(const char *target, const char *name)
{
#ifdef _WIN32
  return CreateSymbolicLinkA(name, target, 2) != 0;
#else
  return symlink(target, name) == 0;
#endif
}
static void record(const char *name, int ok)
{
  fprintf(report, "%s %d errno=%d", name, ok, errno);
#ifdef _WIN32
  fprintf(report, " winerror=%lu", (unsigned long)GetLastError());
#endif
  fputc('\n', report);
}
int main(int argc, char **argv)
{
  char absolute[4096];
  if (argc != 3 || chdir(argv[1]) != 0) return 90;
#ifdef _WIN32
  report = fopen("probe.log", "wb");
#else
  report = stdout;
#endif
  if (!report) return 91;
  if (snprintf(absolute, sizeof(absolute), "%s/absolute", argv[2]) >= (int)sizeof(absolute)) return 92;
  errno = 0;
  record("create", write_byte("inside"));
  record("rename", rename("inside", "renamed") == 0);
  record("hardlink", hardlink("renamed", "inside-hard") && write_byte("inside-hard"));
  record("symlink", symlink_file("renamed", "inside-sym") && write_byte("inside-sym"));
  if (!write_byte("readonly") || chmod("readonly", 0400) != 0) return 93;
  record("readonly_denied", !write_byte("readonly"));
  record("absolute", write_byte(absolute));
  record("traversal", write_byte("../outside/traversal"));
  if (snprintf(absolute, sizeof(absolute), "%s/symlink_escape", argv[2]) >= (int)sizeof(absolute)) return 92;
  record("symlink_escape", symlink_file(absolute, "outside-sym") && write_byte("outside-sym"));
  if (snprintf(absolute, sizeof(absolute), "%s/hardlink_alias", argv[2]) >= (int)sizeof(absolute)) return 92;
  record("hardlink_alias", hardlink(absolute, "outside-hard") && write_byte("outside-hard"));
  if (fclose(report) != 0) return 94;
  return 0;
}
