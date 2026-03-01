# Cyber Portfolio

This repository contains cybersecurity lab work and packet analysis projects focused on identifying malicious email activity from network traffic captures.

## Project: SMTP Phishing Analysis
- Used Wireshark to inspect and filter SMTP traffic from multiple `.pcap` files
- Applied display filters (e.g., `smtp`, `smtp contains "Subject"`) to locate email data
- Reconstructed full email sessions using Follow → TCP Stream
- Identified phishing emails based on threatening content and Bitcoin payment demands
- Extracted malicious sender IP addresses from SMTP headers (`Received: from`)
- Differentiated between internal relay IPs and true sender IPs

Skills demonstrated:
- Network packet analysis  
- Email header inspection  
- Identifying phishing campaigns  
- Basic digital forensics  

Tools:
- Wireshark  
- Ubuntu VM  
- SMTP protocol analysis
