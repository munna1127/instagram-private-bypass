# Instagram Server-Side Authorization Bypass: Private Timeline Exposure

> **Status:** Silently patched by Meta on October 16, 2025. Awaiting official acknowledgment.

## Summary

This repository documents a critical, server-side authorization bypass vulnerability discovered on Instagram in October 2025. The vulnerability allowed a completely unauthenticated attacker to access the private posts, including direct media URLs, of a significant subset of Instagram's private accounts.

The purpose of this archive is to serve as a complete and factual record of the finding, the professional disclosure process, and the subsequent silent patch by Meta.

## The Vulnerability

The bug was a classic server-side authorization failure. It was not a caching issue. The exploitation was a simple, two-step process:

1.  **The Trigger:** An unauthenticated request sent to a private profile URL with a specific set of mobile `User-Agent` headers would trigger an incorrect state on Instagram's servers.
2.  **The Leak:** Once triggered, the server's HTML response would incorrectly embed a JSON object (`polaris_timeline_connection`) containing the private account's entire timeline of posts, including image and video CDN links.

This entire process required **zero authentication** and worked from any IP address. The proof-of-concept script, [`poc.py`](./poc.py), automates this attack.

## Impact and Severity: The Silent Threat

The true severity of this bug lies in its scale and simplicity.

During authorized testing across 7 different private accounts (a mix of aged, new, and test accounts), the vulnerability was **100% reproducible on 2 of them (~28%)**.

While the exact conditions that made an account vulnerable are known only to Meta's engineers, this exploitability rate in a small, controlled sample suggests that the actual number of affected users could easily be in the **millions**.

What made this vulnerability particularly dangerous was its simplicity. It could be discovered and reproduced with basic web debugging tools. This low barrier to entry meant that any malicious actor who stumbled upon it could have automated the mass harvesting of private, sensitive user data with minimal effort.

## Chronology of Events

A complete, detailed timeline of all events—from initial discovery and a wrongfully rejected first report, to the detailed second report, the back-and-forth with Meta's security team, and the final follow-up—is documented in the master timeline file.

## [View the Full Timeline Here](./TIMELINE.md)

---

### Evidence and Artifacts

This repository contains all the evidence required to validate these findings:

*   [`official_communication/`](./official_communication/): Complete, saved HTML archives of both bug bounty tickets, including the initial incorrect rejection.
*   [`network_logs_and_samples/`](./network_logs_and_samples/): Raw network logs, response headers (`X-FB-Debug`), sample HTML responses, and extracted JSON data from both vulnerable and non-vulnerable accounts.
*   [`videos.txt`](./network_logs_and_samples/videos.txt): Links and SHA256 hashes to all video evidence, including the initial PoC, reproduction on a consenting third-party account, and the final video confirming the patch.
*   [`poc.py`](./poc.py): The exact Python script used to automate the exploit.