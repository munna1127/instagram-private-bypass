# Instagram Private Timeline Bypass

**Status:** Reported to Meta | Awaiting Resolution

**Discovered:** October 12, 2025  
**Reporter:** Jatin Banga ([GitHub](https://github.com/jatin-dot-py))
**Severity:** Critical

---

## Responsible Disclosure Notice

This vulnerability has been reported to Meta through their official Bug Bounty program. This repository contains documentation for personal records and is PRIVATE until Meta provides permission for public disclosure.

**Case Number:** 1838100803582037  
**Report Date:** 2025-10-12 04:23 IST  
**Status:** Under Review

---

## Summary

A server-side authorization bypass in Instagram's mobile web interface allows unauthenticated users to access the complete timeline (private posts) of ANY private Instagram account through a single GET request.

### Impact

- **Affected Accounts:** All private Instagram accounts (~500M+ users)
- **Attack Complexity:** Trivial (single GET request)
- **Authentication Required:** None
- **Detection Probability:** Around Zero/ Very Low (very indistinguishable from normal traffic)
- **Exploit Availability:** Proof-of-concept available

### CVSS Score

N/A

---

## Technical Overview

Instagram's mobile web / smaller viewports rendering path embeds private timeline data directly in the HTML response for performance optimization. When specific client hint headers are present, the server includes complete post metadata including direct CDN URLs to private content.

**Root Cause:** Authorization check missing or bypassed in particular web rendering code path.

**Mechanism:**
1. Client sends GET request to `instagram.com/<username>` with mobile like headers
2. Instagram's JS detects small viewport, other parameters, Eg: `user-agent`, `sec-ch-ua-mobile: ?1`, `sec-fetch-site': 'none'`, etc... (FOR EXACT HEADERS REFER TO HEADERS USED IN poc.py )
3. Server sees mobile headers, activates mobile rendering optimization
4. Server embeds `polaris_timeline_connection` JSON in HTML response
5. JSON contains complete timeline with CDN URLs to private posts
6. **Authorization check never performed**

---

## Discovery Context

Discovered while developing [HttpChain](https://github.com/jatin-dot-py/httpchain), an HTTP orchestration framework for API/ Data Extraction/ OSINT workflows. The bug was found during systematic analysis of Instagram's web responses.

---

## Proof of Concept & Video
- Complete Python exploit script
- Detailed reproduction steps
- Sample response
- Link to video: [Video](https://drive.google.com/file/d/1F386Wky80QQBX35-89tmVljHHap6uBGy/view)

---

## Timeline

**Key Dates:**
- **2025-10-12 ~02:00 IST AM:** Initial discovery
- **2025-10-12 03:56 AM IST:** Reported to Meta Bug Bounty
- **2025-10-12 03:56 AM IST:** Confirmation received (Case #1838087146916736)
- **2025-10-12 04:01 AM IST:** Not Applicable Response Received. They misunderstood the issue as cdn caching (Case #1838087146916736)
- **2025-10-12 04:23 AM IST:** Reported to Meta Bug Bounty AGAIN
- **2025-10-12 04:23 AM IST:** Confirmation received (Case #1838100803582037)
- ... More messages (i will add them later)
- **2025-10-16 18:00 PM IST:** Bug no longer works (Silently patched.)

---

## Responsible Disclosure

This vulnerability was disclosed responsibly through Meta's official Bug Bounty program immediately upon discovery. No exploitation beyond ethical testing on researcher's own accounts was performed.

---

## Contact

For questions about this disclosure: [redacted until public disclosure]

---
