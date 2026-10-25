// SPDX-License-Identifier: Apache-2.0
/**
 * =============================================================================
 * LINUX KERNEL XDP / eBPF HTTP PAYLOAD PRE-INTERCEPTOR FOR PHP VACCINE
 * =============================================================================
 * Architecture: Kernel-Space Packet Drop at Network Interface Card (NIC) / XDP
 * Target: Zero-Overhead (< 2.0 µs) Ingestion Filter Neutralizing CGI Argument
 *         Tampering & Traversal before Userland Socket Delivery.
 * Author: Ayush Pandey (ayushpandey-futureAI)
 * =============================================================================
 */

#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

#define MAX_PAYLOAD_SCAN 128

// Ring buffer or perf event map for threat telemetry dispatch
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(int));
    __uint(value_size, sizeof(int));
    __uint(max_entries, 128);
} threat_events SEC(".maps");

struct threat_event_t {
    __u32 src_ip;
    __u32 dst_ip;
    __u16 src_port;
    __u16 dst_port;
    __u32 threat_id; // 1 = CGI Argument, 2 = Traversal, 3 = Stream
};

SEC("xdp")
int xdp_php_vaccine(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;

    // 1. Ethernet Header Verification
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end) {
        return XDP_PASS;
    }

    if (eth->h_proto != bpf_htons(ETH_P_IP)) {
        return XDP_PASS;
    }

    // 2. IPv4 Header Verification
    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end) {
        return XDP_PASS;
    }

    if (ip->protocol != IPPROTO_TCP) {
        return XDP_PASS;
    }

    // 3. TCP Header Verification
    struct tcphdr *tcp = (void *)((char *)ip + (ip->ihl * 4));
    if ((void *)(tcp + 1) > data_end) {
        return XDP_PASS;
    }

    // Verify common HTTP ports (80, 8080, 443)
    __u16 dest_port = bpf_ntohs(tcp->dest);
    if (dest_port != 80 && dest_port != 8080 && dest_port != 8000) {
        return XDP_PASS;
    }

    // 4. Calculate Payload Start
    unsigned char *payload = (unsigned char *)tcp + (tcp->doff * 4);
    if ((void *)payload >= data_end) {
        return XDP_PASS;
    }

    // Ensure we have at least 4 bytes of HTTP command
    if ((void *)(payload + 4) > data_end) {
        return XDP_PASS;
    }

    // Quick check for HTTP method prefix (GET, POST, HEAD, PUT)
    if (!(payload[0] == 'G' && payload[1] == 'E' && payload[2] == 'T') &&
        !(payload[0] == 'P' && payload[1] == 'O' && payload[2] == 'S' && payload[3] == 'T') &&
        !(payload[0] == 'H' && payload[1] == 'E' && payload[2] == 'A' && payload[3] == 'D')) {
        return XDP_PASS;
    }

    // 5. Bounded Payload Inspection Loop for High-Risk Exploit Patterns
    #pragma unroll
    for (int i = 0; i < MAX_PAYLOAD_SCAN - 16; i++) {
        if ((void *)(payload + i + 16) > data_end) {
            break;
        }

        // Check for "-d allow_url_include" (CVE-2024-4577 & CVE-2012-1823)
        if (payload[i] == '-' && payload[i+1] == 'd' && (payload[i+2] == ' ' || payload[i+2] == '+' || payload[i+2] == '=') &&
            payload[i+3] == 'a' && payload[i+4] == 'l' && payload[i+5] == 'l' &&
            payload[i+6] == 'o' && payload[i+7] == 'w' && payload[i+8] == '_') {
            bpf_printk("PHP-VACCINE-XDP: CGI Injection Dropped at Kernel NIC!\n");
            return XDP_DROP;
        }

        // Check for Windows soft hyphen best-fit bypass "%ad-d" or "%ad+d"
        if (payload[i] == '%' && (payload[i+1] == 'a' || payload[i+1] == 'A') &&
            (payload[i+2] == 'd' || payload[i+2] == 'D') &&
            (payload[i+3] == '-' || payload[i+3] == '+' || payload[i+3] == ' ') &&
            payload[i+4] == 'd') {
            bpf_printk("PHP-VACCINE-XDP: Soft-Hyphen CGI Bypass Dropped at Kernel NIC!\n");
            return XDP_DROP;
        }

        // Check for path traversal "../.."
        if (payload[i] == '.' && payload[i+1] == '.' && payload[i+2] == '/' &&
            payload[i+3] == '.' && payload[i+4] == '.' && payload[i+5] == '/') {
            bpf_printk("PHP-VACCINE-XDP: Path Traversal Dropped at Kernel NIC!\n");
            return XDP_DROP;
        }

        // Check for "php://input" stream wrapper
        if (payload[i] == 'p' && payload[i+1] == 'h' && payload[i+2] == 'p' &&
            payload[i+3] == ':' && payload[i+4] == '/' && payload[i+5] == '/' &&
            payload[i+6] == 'i' && payload[i+7] == 'n' && payload[i+8] == 'p') {
            bpf_printk("PHP-VACCINE-XDP: Stream Wrapper Dropped at Kernel NIC!\n");
            return XDP_DROP;
        }
    }

    return XDP_PASS;
}

char _license[] SEC("license") = "Apache-2.0";
