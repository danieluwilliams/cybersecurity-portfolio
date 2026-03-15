# Directory Traversal Attack Lab

This project demonstrates how a directory traversal vulnerability can allow attackers to access unauthorized files on a server.

## Tools Used
- Wireshark
- Bash scripting
- Node.js
- Packet capture analysis

## Attack Overview
A vulnerable FTP/HTTP server allowed users to request files using crafted paths.

Example request:

GET /timmy/passwords.txt HTTP/1.1

This allowed attackers to retrieve sensitive files outside the intended directory.

## Sensitive Files Discovered

- /timmy/passwords.txt → trixie123
- /wanda/reports_original.txt → Earnings are down 1600%
- /cosmo/rocknames.txt → mr. rock

## Attack Script

The `attack.sh` script:

1. Starts the vulnerable server
2. Sends the attack request
3. Prints the server response
4. Stops the server

## Lessons Learned

- Directory traversal vulnerabilities occur when servers fail to sanitize file paths
- Packet capture analysis can reveal unauthorized file access
- Proper server-side validation is critical for security
