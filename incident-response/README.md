Malware Investigation Report (Splunk and Catalyst)
Overview

In this project, I investigated a simulated cyber incident using Splunk and documented the findings in Catalyst. The goal was to act as a CSIRT analyst, identify suspicious activity, analyze indicators of compromise, and confirm whether the file involved was malicious using external sources.

Investigation Summary

The investigation focused on a suspicious file upload event found in Splunk logs. The file, named EvilScript.exe, was uploaded from an internal IP address. The event included useful details such as the filename, file hash, timestamp, and user agent, which helped build context around the activity.

Key Findings
Artifact Identified
File Name: EvilScript.exe
File Hash: 3AADBF7E527FC1A050E1C97FEA1CBA4D
Source IP: 192.168.1.10
Event Type: File upload with successful HTTP response (200)
External Threat Intelligence

The file hash was analyzed using VirusTotal. The results showed that the file is considered malicious by multiple security vendors. It was identified as a trojan dropper/downloader and was associated with obfuscated macro behavior.

The analysis indicated that the file was capable of:

Decoding hidden payloads
Running system commands
Creating persistence on a system
Downloading and executing additional malicious files

Multiple antivirus engines flagged it as malicious, which confirmed that the file was not safe and likely part of a malware infection attempt.

Catalyst Documentation

The incident was recorded in Catalyst as a malware investigation case. The main artifacts, related behaviors, and supporting evidence from Splunk were added. External validation from VirusTotal was also included to support the findings and confirm the severity of the file.

Lessons Learned
What was done well

Splunk provided enough detail to clearly identify the suspicious file upload, including the file hash and source IP address. Using VirusTotal helped confirm that the file was malicious, which made the investigation more reliable.

What could have been done better

The system did not block the malicious file at the time of upload. There was no real-time scanning or prevention in place, which allowed the file to be accepted without being flagged immediately.

Improvements for the future

To prevent similar incidents, file uploads should be scanned in real time for malware before being accepted. Executable files should be restricted or heavily monitored. Endpoint detection and response tools should also be implemented to detect malicious behavior after execution. In addition, better SIEM alerting rules could help catch suspicious file activity earlier.

Conclusion

Overall, the investigation showed how a malicious file can enter a system through a simple upload event and how tools like Splunk and VirusTotal can be used together to detect and confirm threats. It also highlighted the importance of proactive monitoring and stronger security controls to prevent similar incidents.
