// SPDX-License-Identifier: Apache-2.0
/**
 * =============================================================================
 * LINUX KERNEL eBPF WORKER PROCESS MEMORY & EXPLOIT QUARANTINE PROBE
 * =============================================================================
 * Tracks exploit violation frequency per PHP worker thread (PID).
 * Automatically signals userspace quarantine manager when attack threshold is breached.
 * Author: Ayush Pandey (ayushpandey-futureAI)
 * =============================================================================
 */

#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>

#define QUARANTINE_THRESHOLD 5

struct worker_stat_t {
    __u32 pid;
    __u32 violation_count;
    __u64 last_violation_ns;
    __u32 is_quarantined;
};

// Map storing worker statistics: PID -> worker_stat_t
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(key_size, sizeof(__u32));
    __uint(value_size, sizeof(struct worker_stat_t));
    __uint(max_entries, 1024);
} worker_quarantine_map SEC(".maps");

SEC("kprobe/sys_enter")
int trace_worker_exploit(struct pt_regs *ctx) {
    __u64 pid_tgid = bpf_get_current_pid_tgid();
    __u32 pid = pid_tgid >> 32;

    struct worker_stat_t *stat = bpf_map_lookup_elem(&worker_quarantine_map, &pid);
    if (!stat) {
        struct worker_stat_t init_stat = {
            .pid = pid,
            .violation_count = 1,
            .last_violation_ns = bpf_ktime_get_ns(),
            .is_quarantined = 0
        };
        bpf_map_update_elem(&worker_quarantine_map, &pid, &init_stat, BPF_ANY);
        return 0;
    }

    stat->violation_count++;
    stat->last_violation_ns = bpf_ktime_get_ns();

    if (stat->violation_count >= QUARANTINE_THRESHOLD) {
        stat->is_quarantined = 1;
        bpf_printk("PHP-VACCINE-QUARANTINE: Worker PID %d placed into quarantine (Violations: %d)\n",
                   pid, stat->violation_count);
    }

    return 0;
}

char _license[] SEC("license") = "Apache-2.0";
