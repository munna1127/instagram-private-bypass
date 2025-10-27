# Timeline: Instagram Server-Side Authorization Bypass Vulnerability
*   **Researcher:** Jatin
*   **Vulnerability:** Server-Side Authorization Bypass in Instagram's mobile web interface, returning private timeline data to unauthenticated requests.
*   **Status:** Silently patched by Meta on October 16, 2025. Awaiting official acknowledgment.

---

## Summary

This document provides a complete chronological record of the discovery, reporting, and eventual silent patching of a critical privacy vulnerability on Instagram. The vulnerability allowed any unauthenticated user to access the private posts, including direct CDN links to media, for subset of private Instagram account by sending a request with specific mobile headers.

All official communication with Meta is archived and can be reviewed in the [`official_communication/`](./official_communication/) directory. All video evidence is detailed in [`videos.txt`](./network_logs_and_samples/videos.txt).

---

### **October 12, 2025: Initial Discovery and Incorrect Rejection**

My investigation began with the discovery that private Instagram profile data was being leaked in the HTML response to unauthenticated requests.

*   **~22:26 UTC (Oct 12, 03:56 IST):** Submitted the initial report to Meta's bug bounty program.
    *   **Case Number:** `1838087146916736`
    *   **Evidence:** The initial report details can be viewed in the full communication log: [`official_communication/Case_1838087146916736_v1.html`](./official_communication/Case_1838087146916736_v1.html).

*   **22:31 UTC (Oct 12, 04:01 IST):** The report was quickly closed by Meta. The team misinterpreted the server-side authorization bypass as an expected CDN caching issue, stating they have no control over it.
    *   **Meta's Rationale:** *"Your report describes one of the scenarios that we do not have any control over."*
    *   **Evidence:** See Meta's full response in [`official_communication/Case_1838087146916736_v1.html`](./official_communication/Case_1838087146916736_v1.html).

### **October 12, 2025: Second, More Detailed Report**

Recognizing the misunderstanding, I immediately filed a new, more detailed report with clearer terminology, emphasizing that this was a **server-side authorization failure**, not a client-side or CDN caching problem.

*   **22:53 UTC (Oct 12, 04:23 IST):** Submitted a new, comprehensive report.
    *   **Case Number:** `1838100803582037`
    *   **Title:** "Server-Side Authorization Bypass: Instagram Mobile Web Returns Private Timeline Data to Unauthenticated Requests"
    *   **Evidence:** The complete report and all subsequent communication are archived in [`official_communication/Case_1838100803582037_v1.html`](./official_communication/Case_1838100803582037_v1.html).
    *   **Supporting Code:** The proof-of-concept script submitted is available at [`poc.py`](./poc.py).
    *   **Initial Video Proof:** The first video demonstrating the exploit was submitted. See **Video 1** in [`videos.txt`](./network_logs_and_samples/videos.txt).

### **October 13, 2025: Initial Triage and Investigation**

Meta's security team began the triage process, requesting tests on their accounts.

*   **07:23 UTC (12:53 IST):** Meta (Julian) requested I test the vulnerability on their test account, `2fa_2fa`.
*   **09:20 UTC (14:50 IST):** I replied, confirming the exploit did **not** work on `2fa_2fa` but was still **100% reproducible** on my aged, private test account. This provided the first clue that account characteristics (like age) were a factor.
    *   **Evidence:** A video demonstrating the failed test on `2fa_2fa` and a successful re-test on my account was provided. See **Video 2** in [`videos.txt`](./network_logs_and_samples/videos.txt).
    *   **Evidence:** An example of the non-vulnerable response headers and an empty JSON snippet from this test can be found in [`network_logs_and_samples/unexploted_headers.txt`](./network_logs_and_samples/unexploted_headers.txt) and [`network_logs_and_samples/sample_empty_json_snippet_exposing_no_posts.json`](./network_logs_and_samples/sample_empty_json_snippet_exposing_no_posts.json).

### **October 14, 2025: Reproducibility Challenge and Breakthrough**

The investigation continued, with Meta's team initially unable to reproduce the issue.

*   **12:37 UTC (18:07 IST):** Meta (Sarah) stated they were unable to reproduce the bug with their own aged accounts and requested a new PoC on another account besides `@jatin.py`.
*   **15:15 UTC (20:45 IST):** I provided a critical breakthrough. I successfully reproduced the vulnerability on a **second, consenting third-party account** (`its_prathambanga`), proving the issue was not isolated to my own account.
    *   **Evidence:** A new video showing both manual and script-based reproduction on this new account was provided. See **Video 3** in [`videos.txt`](./network_logs_and_samples/videos.txt).
    *   **Evidence:** Network logs from the successful exploit on this consenting account are documented in [`network_logs_and_samples/exploited_headers_links_2.txt`](./network_logs_and_samples/exploited_headers_links_2.txt).

### **October 15, 2025: Final Analysis and Reproduction Pattern**

To eliminate any remaining ambiguity, I sent a final, detailed analysis that provided a clear, two-step pattern for reliably reproducing the vulnerability.

*   **14:53 UTC (20:23 IST):** I sent a message detailing the two-part behavior:
    1.  **The Trigger:** Using specific mobile headers triggers a state where the server incorrectly reports `follower_count` and `following_count` as 0 in the UI.
    2.  **The Vulnerability:** Once in this state, the server proceeds to incorrectly populate the `polaris_timeline_connection` object in the embedded JSON with private post data.
    *   **Evidence:** This detailed explanation is logged in the main communication file: [`official_communication/Case_1838100803582037_v1.html`](./official_communication/Case_1838100803582037_v1.html).
    *   **Visual Proof:** The following screenshot clearly shows both the "Trigger" (0 followers/following in the UI) and the "Vulnerability" (private timeline data populated in the JSON) occurring simultaneously in an unauthenticated session.
        *   **File:** [`screenshots/Screenshot 2025-10-17 213244.png`](./screenshots/Screenshot%202025-10-17%20213244.png)
        *   ![Proof of Vulnerability](./screenshots/Screenshot%202025-10-17%20213244.png)
    *   **Supporting Evidence:** An example of a vulnerable HTML response and the extracted JSON data can be reviewed at [`network_logs_and_samples/sample_html_response_1.html`](./network_logs_and_samples/sample_html_response_1.html) and [`network_logs_and_samples/sample_extracted_json_snippet_exposing_post_data.json`](./network_logs_and_samples/sample_extracted_json_snippet_exposing_post_data.json).


### **October 16, 2025: The Silent Patch**

After providing the definitive reproduction steps, the vulnerability was patched without any notification from Meta.

*   **~12:30 UTC (18:00 IST):** During routine re-testing, I discovered the vulnerability was no longer reproducible. The exploit failed on all previously vulnerable accounts.
    *   **Evidence:** A timestamped screen recording was made to document that the previously successful methods no longer worked, confirming the fix. See **Video 4** in [`videos.txt`](./network_logs_and_samples/videos.txt).

### **October 17, 2025: Follow-up and Awaiting Acknowledgment**

Having confirmed the patch, I sent a follow-up to Meta to notify them of my observation and request confirmation.

*   **14:36 UTC (20:06 IST):** Sent a message to the Meta Security Team confirming that the bug appeared to be fixed and requested a status update.
    *   **Evidence:** See the final entry in the communication log: [`official_communication/Case_1838100803582037_v1.html`](./official_communication/Case_1838100803582037_v1.html).

As of the last update to this document, there has been no official acknowledgment of the report's validity or the patch from Meta.
