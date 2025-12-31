import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText
import requests, socket, re, dns.resolver, whois, threading
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- CONFIG ----------------
DEVELOPER_INFO = {
    "name":     "GopalakrishnaVarma",
    "role":     "Pentester",
    "tool":     "WEB-Recon",
    "version":  "1.0",
    "Email":  "gopalakrisna89779@gmail.com",
    "github":   "https://github.com/gopalakrishnsak/",
    "TryHackMe":"https://tryhackme.com/p/gopalakrishnavarma/" ,
    "LinkedIn":"https://www.linkedin.com/in/gopalakrishnavarma/"
}

CRAWL_PATHS = ["", "contact", "about", "support", "contact-us", "about-us"]
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
SUBDOMAINS = ["www","mail","webmail","smtp","pop","imap","ftp","sftp","ssh","vpn","remote",
"portal","login","auth","account","accounts","admin","administrator","admins","root",
"dashboard","panel","cpanel","whm","billing","payments","pay","secure","ssl",
"api","api-dev","api-test","api-stage","api-staging","api-prod",
"rest","graphql","soap","v1","v2","v3",
"dev","test","testing","stage","staging","uat","preprod","prod","beta","alpha",
"internal","intranet","extranet","private","public",
"cdn","cdn1","cdn2","static","static1","static2","assets","img","images","media",
"files","upload","downloads",
"docs","doc","wiki","kb","help","support","status","health","monitor","metrics",
"logs","log","backup","backups","old","archive","legacy","deprecated","new","temp","tmp",
"sandbox","lab","labs","research","demo","demos","preview",
"blog","blogs","news","forum","forums","community","chat","irc",
"email","mx","ns","ns1","ns2","dns",
"search","shop","store","cart","checkout","order","orders","payment","payments",
"crm","erp","hr","hrms","finance","accounting",
"jira","confluence",
"git","gitlab","github","bitbucket","repo","repos","svn",
"ci","cd","jenkins","build","builds","deploy","deployment",
"docker","registry","k8s","kubernetes",
"monitoring","grafana","prometheus","elk","kibana","siem","splunk",
"sso","oauth","openid","id","identity",
"auth-dev","auth-test","auth-stage","auth-prod",
"mobile","m","app","apps","ios","android","push","notify","notifications",
"websocket","ws","socket",
"edge","gateway","proxy","reverse-proxy","loadbalancer","lb",
"fw","firewall","waf"
]
OBFUSCATED = [
    (r"\s*\[at\]\s*", "@"),
    (r"\s*\(at\)\s*", "@"),
    (r"\s+AT\s+", "@"),
    (r"\s*\[dot\]\s*", "."),
    (r"\s*\(dot\)\s*", "."),
    (r"\s+DOT\s+", ".")
]

def run_threaded(func):
    def wrapper():
        output.delete(1.0, tk.END)
        output.insert(tk.END, "[*] Working... Please wait\n\n")
        threading.Thread(target=func, daemon=True).start()
    return wrapper

def developer_info():
    output.delete(1.0, tk.END)
    output.insert(tk.END, "Developed-By\n\n")
    for k, v in DEVELOPER_INFO.items():
        output.insert(tk.END, f"{k.title():<10}: {v}\n")

# ---------------- HELPERS ----------------
def normalize(text):
    for pat, rep in OBFUSCATED:
        text = re.sub(pat, rep, text, flags=re.I)
    return text

def extract_data(text, emails, phones):
    text = normalize(text)
    emails.update(re.findall(EMAIL_REGEX, text))
    phones.update(re.findall(PHONE_REGEX, text))

# ---------------- CORE ----------------
def full_email_phone_extraction():
    target = entry.get().rstrip("/")
    domain = target.replace("https://","").replace("http://","").split("/")[0]

    emails, phones = set(), set()
    output.delete(1.0, tk.END)

    for path in CRAWL_PATHS:
        try:
            url = f"{target}/{path}" if path else target
            r = requests.get(url, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")

            extract_data(soup.get_text(), emails, phones)

            # --- JavaScript files ---
            for js in soup.find_all("script"):
                if js.string:
                    extract_data(js.string, emails, phones)
                elif js.get("src"):
                    try:
                        js_url = js["src"]
                        if js_url.startswith("/"):
                            js_url = target + js_url
                        js_code = requests.get(js_url, timeout=5).text
                        extract_data(js_code, emails, phones)
                    except:
                        pass
        except:
            pass

    try:
        w = whois.whois(domain)
        extract_data(str(w), emails, phones)
    except:
        pass

    output.insert(tk.END, "Emails Found:\n")
    for e in sorted(emails) or ["None"]:
        output.insert(tk.END, f"{e}\n")

    output.insert(tk.END, "\nPhone Numbers Found:\n")
    for p in sorted(phones) or ["None"]:
        output.insert(tk.END, f"{p}\n")

def website_info():
    output.delete(1.0, tk.END)
    try:
        r = requests.get(entry.get(), timeout=5)
        output.insert(tk.END, f"Status: {r.status_code}\nServer: {r.headers.get('Server')}\n\nHeaders:\n{r.headers}")
    except Exception as e:
        output.insert(tk.END, str(e))

def dns_info():
    output.delete(1.0, tk.END)
    domain = entry.get().replace("https://","").replace("http://","")
    try:
        for t in ["A","MX","NS","TXT","CAA","SOA","HTTPS"]:
            output.insert(tk.END, f"\n{t} Records:\n")
            for r in dns.resolver.resolve(domain, t):
                output.insert(tk.END, str(r)+"\n")
        output.insert(tk.END, f"\nWHOIS:\n{whois.whois(domain)}")
    except Exception as e:
        output.insert(tk.END, str(e))


def ip_ports():
    output.delete(1.0, tk.END)

    host = entry.get().replace("https://", "").replace("http://", "").strip()

    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        output.insert(tk.END, "Invalid host\n")
        return

    output.insert(tk.END, f"IP: {ip}\n\nOpen Ports (TCP):\n")

    # Port : Service mapping
    ports = {
    21: "FTP",22: "SSH",23: "Telnet",25: "SMTP",53: "DNS",67: "DHCP",68: "DHCP",69: "TFTP",80: "HTTP",
    110: "POP3",111: "RPC",123: "NTP",135: "MSRPC",137: "NetBIOS",138: "NetBIOS",139: "NetBIOS",143: "IMAP",161: "SNMP",162: "SNMP Trap",
    389: "LDAP",443: "HTTPS",445: "SMB",465: "SMTPS",500: "ISAKMP",514: "Syslog",520: "RIP",587: "SMTP",636: "LDAPS",
    993: "IMAPS",995: "POP3S",1433: "MSSQL",1521: "Oracle",1900: "SSDP",
    2049: "NFS",2082: "cPanel",2083: "cPanel SSL",2086: "WHM",2087: "WHM SSL",2181: "Zookeeper",2375: "Docker",2379: "etcd",2483: "Oracle SSL",
    3000: "Dev Apps",3306: "MySQL",3389: "RDP",
    4444: "Metasploit",4500: "IPsec NAT-T",
    5353: "mDNS",5432: "PostgreSQL",5601: "Kibana",5900: "VNC",5985: "WinRM", 5986: "WinRM SSL",
    6379: "Redis",7001: "WebLogic",
    8000: "HTTP-Alt", 8008: "HTTP-Alt", 8080: "HTTP Proxy",8081: "Admin",8443: "HTTPS-Alt",
    9000: "PHP-FPM", 9042: "Cassandra",9200: "Elasticsearch",9418: "Git", 27017: "MongoDB"
    }

    for port, service in ports.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)

        if s.connect_ex((ip, port)) == 0:
            output.insert(
                tk.END,
                f"Port {port:<5} OPEN  →  {service} (TCP)\n"
            )

        s.close()

#-------ADMIN-FINDER------

def admin_finder():
    url = entry.get()
    output.delete(1.0, tk.END)
    paths = ["/admin","/administrator","/adminpanel","/admin-panel","/admin_area","/adminarea",
"/admin/login","/admin/logon","/admin/index","/admin/home","/admin/dashboard",
"/admins","/admin1","/admin2","/admin3","/admin4","/admin5",
"/admin-old","/admin-old/login","/admin-backup","/admin.bak",
"/admin.php","/admin.html","/admin.jsp","/admin.aspx",
"/login","/logon","/signin","/sign-in","/auth","/auth/login",
"/user/login","/users/login","/account/login","/accounts/login",
"/secure","/secure/login","/security","/security/login",
"/dashboard","/dashboard/login","/dashboard/admin",
"/control","/controlpanel","/control-panel","/cp","/cpanel","/whm",
"/panel","/panel/login","/panel/admin","/manage","/management",
"/backend","/backend/login","/backoffice","/backoffice/login",
"/office","/office/login","/staff","/staff/login","/employee/login",
"/root","/root/login","/sys","/system","/system/login",
"/sysadmin","/sys-admin","/superadmin","/super-admin",
"/private","/private/login","/internal","/internal/login",
"/intranet","/intranet/login",
"/console","/console/login","/adminconsole","/webconsole",
"/server","/server-status","/server-info",
"/config","/configuration","/settings","/settings/login",
"/setup","/install","/installation","/installer",
"/update","/upgrade","/maintenance",
"/db","/database","/dbadmin","/phpmyadmin","/phpMyAdmin",
"/mysql","/mysqladmin","/pma","/adminer",
"/cms","/cms/login","/cms/admin",
"/wp-admin","/wp-login.php",
"/wp-admin/install.php","/wp-admin/setup-config.php",
"/joomla/administrator","/administrator/index.php",
"/drupal/admin","/drupal/login",
"/magento/admin","/magento/adminhtml",
"/shop/admin","/store/admin",
"/laravel/admin","/symfony/admin",
"/rails/admin","/django/admin",
"/api/admin","/api/login","/api/auth",
"/rest/admin","/graphql/admin",
"/test/admin","/testing/admin","/dev/admin","/staging/admin",
"/beta/admin","/old/admin","/backup/admin",
"/hidden","/hidden/admin","/secret","/secret/admin",
"/admin~","/~admin","/.admin","/_admin",
"/admin.zip","/admin.tar","/admin.tar.gz","/admin.rar",
"/login.php","/login.html","/login.aspx","/login.jsp",
"/admin/login.php","/admin/login.html","/admin/login.aspx",
"/signin.php","/auth.php","/auth/login.php",
"/user.php","/users.php",
"/manager","/manager/html","/host-manager",
"/jenkins","/jenkins/login",
"/grafana","/grafana/login",
"/kibana","/kibana/login",
"/prometheus","/splunk","/splunk/login",
"/vault","/vault/login",
"/git","/gitlab","/gitlab/admin",
"/repo","/repos",
"/monitor","/monitoring","/status","/health",
"/metrics","/logs","/logviewer",
"/support","/helpdesk","/ticket","/tickets",
"/crm/admin","/erp/admin","/hr/admin"]
    try:
        for p in paths:
            full = f"{url}/{p}"
            r = requests.get(full, timeout=5)
            if r.status_code in [200,301,302]:
                output.insert(tk.END, f"Found: {full}\n")
    except Exception as e:
        output.insert(tk.END, str(e))


def subdomain_finder():
    output.delete(1.0, tk.END)
    domain = entry.get().replace("https://","").replace("http://","").split("/")[0]

    found = []
    for sub in SUBDOMAINS:
        try:
            host = f"{sub}.{domain}"
            socket.gethostbyname(host)
            found.append(host)
        except:
            pass

    output.insert(tk.END, "Subdomains Found:\n")
    for s in found or ["None"]:
        output.insert(tk.END, f"{s}\n")
        ("Subdomains", subdomain_finder)
         
      
#-------------ROBOT_TXT-Finder______
def robots_txt():
    output.delete(1.0, tk.END)
    url = entry.get().rstrip("/") + "/robots.txt"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            output.insert(tk.END, r.text)
        else:
            output.insert(tk.END, "robots.txt not found")
    except Exception as e:
        output.insert(tk.END, str(e))
        
        
# ---------------- EXPORT ----------------
def export_report(fmt):
    text = output.get(1.0, tk.END)
    file = filedialog.asksaveasfilename(defaultextension=f".{fmt}")
    if not file:
        return

    if fmt == "txt":
        open(file,"w").write(text)

    elif fmt == "html":
        open(file,"w").write(f"<pre>{text}</pre>")

    elif fmt == "pdf":
        doc = SimpleDocTemplate(file)
        styles = getSampleStyleSheet()
        doc.build([Paragraph(text.replace("\n","<br/>"), styles["Normal"])])

def table(title, headers, rows):
    line = "+" + "+".join(["-"*20]*len(headers)) + "+\n"
    out = f"\n{title}\n{line}"
    out += "|" + "|".join(h.center(20) for h in headers) + "|\n" + line
    for r in rows:
        out += "|" + "|".join(str(c).ljust(20)[:20] for c in r) + "|\n"
    return out + line

##-------------CONTACT----ADMIN---------

def ip_intelligence():
    output.delete(1.0, tk.END)

    target = entry.get().replace("https://", "").replace("http://", "").strip()

    try:
        ip = socket.gethostbyname(target)
    except:
        output.insert(tk.END, "Invalid domain or IP\n")
        return

    output.insert(tk.END, f"Target IP: {ip}\n\n")

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,lat,lon,timezone,isp,org,as,query"
        data = requests.get(url, timeout=5).json()

        if data["status"] != "success":
            output.insert(tk.END, "IP intelligence lookup failed\n")
            return

        output.insert(tk.END, "🌍 GeoIP Information\n")
        output.insert(tk.END, "-"*40 + "\n")
        output.insert(tk.END, f"Country     : {data.get('country')}\n")
        output.insert(tk.END, f"Region      : {data.get('regionName')}\n")
        output.insert(tk.END, f"City        : {data.get('city')}\n")
        output.insert(tk.END, f"Latitude    : {data.get('lat')}\n")
        output.insert(tk.END, f"Longitude   : {data.get('lon')}\n")
        output.insert(tk.END, f"Timezone    : {data.get('timezone')}\n\n")

        output.insert(tk.END, "🏢 Network / ASN Information\n")
        output.insert(tk.END, "-"*40 + "\n")
        output.insert(tk.END, f"ISP         : {data.get('isp')}\n")
        output.insert(tk.END, f"Organization: {data.get('org')}\n")
        output.insert(tk.END, f"ASN         : {data.get('as')}\n")

        try:
            ptr = socket.gethostbyaddr(ip)[0]
            output.insert(tk.END, f"Reverse DNS : {ptr}\n")
        except:
            output.insert(tk.END, "Reverse DNS : Not found\n")

    except Exception as e:
        output.insert(tk.END, f"Error: {e}\n")

##------My-IP-----

def my_ip_info():
    output.delete(1.0, tk.END)

    try:
        # Step 1: Get public IP
        ip = requests.get("https://api.ipify.org", timeout=5).text.strip()

        output.insert(tk.END, "🧑‍💻 Your IP Information\n\n")
        output.insert(tk.END, f"IP Address : {ip}\n\n")

        # Step 2: Try ipapi.co first
        geo = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5).json()

        # If ipapi.co fails, fallback to ip-api.com
        if geo.get("error") or geo.get("country_name") is None:
            geo = requests.get(
                f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,lat,lon,timezone,isp,org,as",
                timeout=5
            ).json()

            if geo.get("status") != "success":
                output.insert(tk.END, "GeoIP lookup failed\n")
                return

            country = geo.get("country")
            region = geo.get("regionName")
            city = geo.get("city")
            lat = geo.get("lat")
            lon = geo.get("lon")
            tz = geo.get("timezone")
            isp = geo.get("isp")
            asn = geo.get("as")

        else:
            country = geo.get("country_name")
            region = geo.get("region")
            city = geo.get("city")
            lat = geo.get("latitude")
            lon = geo.get("longitude")
            tz = geo.get("timezone")
            isp = geo.get("org")
            asn = geo.get("asn")

        # Step 3: Output
        output.insert(tk.END, "🌍 GeoIP Information\n")
        output.insert(tk.END, "-" * 40 + "\n")
        output.insert(tk.END, f"Country     : {country}\n")
        output.insert(tk.END, f"Region      : {region}\n")
        output.insert(tk.END, f"City        : {city}\n")
        output.insert(tk.END, f"Latitude    : {lat}\n")
        output.insert(tk.END, f"Longitude   : {lon}\n")
        output.insert(tk.END, f"Timezone    : {tz}\n\n")

        output.insert(tk.END, "🏢 Network / ASN Information\n")
        output.insert(tk.END, "-" * 40 + "\n")
        output.insert(tk.END, f"ISP         : {isp}\n")
        output.insert(tk.END, f"ASN         : {asn}\n")

        try:
            ptr = socket.gethostbyaddr(ip)[0]
            output.insert(tk.END, f"Reverse DNS : {ptr}\n")
        except:
            output.insert(tk.END, "Reverse DNS : Not found\n")

    except Exception as e:
        output.insert(tk.END, f"Error: {e}\n")





# ---------------- GUI----------------
app = tk.Tk()
app.title("WEB-Info")
app.geometry("900x600")
app.configure(bg="#000102")

style = ttk.Style()
style.theme_use("default")

style.configure("TButton", background="#000000", foreground="#00ea8c")
style.configure("TLabel", background="#0f172a", foreground="#00ea8c")
style.configure("TEntry", fieldbackground="#1e293b", foreground="#00ea8c")

ttk.Label(app, text="Target URL / Domain").pack(pady=0)
entry = ttk.Entry(app, width=90)
entry.pack()

btns = ttk.Frame(app)
btns.pack(pady=3)

for txt, cmd in [
  
    ("[RobotTXT]", run_threaded(robots_txt)),
    ("Admin Finder", run_threaded(admin_finder)),
    ("[Subdomain Finder]", run_threaded(subdomain_finder)),
    ("[Web-Info&Tech]", run_threaded(website_info))
]:
    ttk.Button(btns, text=txt, command=cmd).pack(side=tk.LEFT, padx=0)
for txt, cmd in [
    
    ("[DNS & Whois] ", run_threaded(dns_info)),
    ("[Emails & Phones]", run_threaded(full_email_phone_extraction)),
    ("[IP & Ports]",run_threaded( ip_ports)),
    ("[Developer Info]", run_threaded(developer_info)),
    ("[My IP Info]", run_threaded(my_ip_info)),
     ("[IP Intelligence]", run_threaded(ip_intelligence))
  
 ]:   
 ttk.Button(btns, text=txt, command=cmd).pack(side=tk.LEFT, padx=0)

##--------

export = ttk.Frame(app)
export.pack(pady=0)
ttk.Button(export, text="Export TXT", command=lambda: export_report("txt")).pack(side=tk.LEFT, padx=0)
ttk.Button(export, text="Export HTML", command=lambda: export_report("html")).pack(side=tk.LEFT, padx=0)
ttk.Button(export, text="Export PDF", command=lambda: export_report("pdf")).pack(side=tk.LEFT, padx=0)

output = ScrolledText(app, bg="#000000", fg="#09e82e", insertbackground="#00c7ea")
output.pack(expand=True, fill="both", padx=0, pady=0)

app.mainloop()
