# WEB-Recon-GUI

# Web Info Recon
 Web Reconnaissance Tool written in Python.

## Features
- Subdomain Enumeration
- Port Scanning with Protocol Detection
- Target IP Intelligence (ASN, ISP, Geo)
- Tkinter GUI
##DNS & WHOIS Enumeration
- DNS records:
  - A, MX, NS, TXT, CAA, SOA, HTTPS
- WHOIS lookup:
  - Domain registrar
  - Ownership details
  - Abuse & admin contacts
##Subdomain Enumeration
- Wordlist-based subdomain discovery
- Detects:
  - Admin portals
  - APIs
  - Dev / Test / Staging environments
  - CDN and static hosts
- DNS resolution-based validation
  ##Admin Panel Finder
- Large admin/login path wordlist
- CMS detection:
  - WordPress, Joomla, Drupal
- Framework & DevOps panels:
  - Laravel, Django, Jenkins, Grafana, Kibana
- Detects HTTP 200 / 301 / 302 responses
##IP & Port Scanning
- Domain-to-IP resolution
- TCP port scanning
- Service identification for 50+ common ports:
  - Web (HTTP/HTTPS alt ports)
  - Databases (MySQL, PostgreSQL, MongoDB, MSSQL)
  - DevOps (Docker, Kubernetes, Redis)
  - Windows services (RDP, SMB, WinRM)
##robots.txt Analyzer
- Automatically fetches and displays `/robots.txt`
- Reveals hidden or restricted paths
## Report Export
- Export results in:
  - TXT
  - HTML
  - PDF (optional)
  
## Installation
```bash
git clone https://github.com/gopalakrishnsak/WEB-Recon.git
cd WEB-Recon
pip install -r requirements.txt

for kali try this 
pipx install -r requirements.txt
python3 webrecon.py





NOTE:must use https:// or http://
EX: https://domain.con
