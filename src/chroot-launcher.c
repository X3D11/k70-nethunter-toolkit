#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

/* All mounts happen after verified unshare and recursive private propagation. */
static const char *root = "/data/local/codex-nethunter/kali-arm64";
static void die(const char *s) { perror(s); exit(1); }
static void namespace_id(char *buf, size_t len) {
    ssize_t n = readlink("/proc/self/ns/mnt", buf, len - 1);
    if (n < 0) die("namespace readlink");
    buf[n] = 0;
}
static void private_check(void) {
    FILE *f = fopen("/proc/self/mountinfo", "r");
    if (!f) die("mountinfo");
    char *line = NULL; size_t len = 0;
    while (getline(&line, &len, f) >= 0)
        if (strstr(line, " shared:") || strstr(line, " master:")) {
            fprintf(stderr, "Refusing shared/slave mount namespace\n"); exit(1);
        }
    free(line); fclose(f);
}
static void path(char *buf, size_t len, const char *suffix) {
    if (snprintf(buf, len, "%s%s", root, suffix) >= (int)len) exit(1);
}
static void dir(const char *p, mode_t mode) {
    if (mkdir(p, mode) && errno != EEXIST) die(p);
}
static void node(const char *suffix, unsigned int minor_num) {
    char p[512]; path(p, sizeof(p), suffix);
    dev_t device = (1U << 8) | minor_num;
    if (mknod(p, S_IFCHR | 0666, device)) die("mknod");
    if (chmod(p, 0666)) die("chmod device");
    struct stat st;
    if (stat(p, &st) || !S_ISCHR(st.st_mode) || st.st_rdev != device) {
        fprintf(stderr, "Invalid private device %s\n", p); exit(1);
    }
}
int main(int argc, char **argv) {
    if (argc < 2 || getuid() != 0) return 2;
    /* Drop Magisk's inherited OOM immunity for this task and its descendants. */
    int oom = open("/proc/self/oom_score_adj", O_WRONLY | O_CLOEXEC);
    if (oom < 0 || write(oom, "500\n", 4) != 4) die("task OOM priority");
    if (close(oom)) die("close OOM priority");
    char before[128], after[128], p[512];
    namespace_id(before, sizeof(before));
    if (unshare(CLONE_NEWNS)) die("unshare");
    namespace_id(after, sizeof(after));
    if (!strcmp(before, after)) { fprintf(stderr, "Namespace unchanged\n"); return 1; }
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL)) die("private namespace");
    private_check();
    fprintf(stderr, "Private mount namespace verified: %s -> %s\n", before, after);
    if (argc == 2 && !strcmp(argv[1], "--check-namespace")) return 0;
    umask(0);
    path(p, sizeof(p), "/dev");
    if (mount("tmpfs", p, "tmpfs", MS_NOSUID, "mode=0755")) die("private dev");
    node("/dev/null", 3); node("/dev/zero", 5); node("/dev/full", 7);
    node("/dev/random", 8); node("/dev/urandom", 9);
    path(p, sizeof(p), "/proc");
    if (mount("proc", p, "proc", MS_RDONLY|MS_NOSUID|MS_NODEV|MS_NOEXEC, NULL)) die("private proc");
    path(p, sizeof(p), "/dev/shm"); dir(p, 01777);
    if (mount("tmpfs", p, "tmpfs", MS_NOSUID|MS_NODEV, "mode=1777")) die("private shm");
    path(p, sizeof(p), "/dev/pts"); dir(p, 0755);
    if (mount("devpts", p, "devpts", MS_NOSUID|MS_NOEXEC, "newinstance,ptmxmode=0666,mode=0620")) die("private pts");
    path(p, sizeof(p), "/dev/ptmx"); if (symlink("pts/ptmx", p)) die("ptmx");
    path(p, sizeof(p), "/dev/fd"); if (symlink("/proc/self/fd", p)) die("fd");
    private_check();
    umask(0022);
    if (chroot(root) || chdir("/")) die("chroot");
    clearenv();
    setenv("HOME", "/root", 1); setenv("USER", "root", 1);
    setenv("LOGNAME", "root", 1); setenv("LANG", "C.UTF-8", 1);
    setenv("TERM", "xterm-256color", 1);
    setenv("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", 1);
    execvp(argv[1], argv + 1); die("exec");
}
