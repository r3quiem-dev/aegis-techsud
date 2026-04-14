import subprocess
import json
import csv
import datetime
import socket
import os

def get_active_services():

    print("[*] Inventaire des services actifs...")
    
    result = subprocess.run(
        ["systemctl", "list-units", "--type=service", 
         "--state=active", "--no-pager", "--no-legend"],
        capture_output=True,
        text=True
    )
    
    services = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            parts = line.split()
            if len(parts) >= 4:
                services.append({
                    "name": parts[0],
                    "load": parts[1],
                    "active": parts[2],
                    "sub": parts[3]
                })
    
    print(f"[+] {len(services)} services actifs trouvés")
    return services

if __name__ == "__main__":
    services = get_active_services()
    for s in services[:5]:
        print(f"  → {s['name']} ({s['sub']})")

def get_open_ports():

    print("[*] Vérification des ports ouverts...")
    
    result = subprocess.run(
        ["ss", "-tlnp"],
        capture_output=True,
        text=True
    )
    
    ports = []
    lines = result.stdout.strip().split('\n')[1:]
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) >= 4:
                local_address = parts[3]
                port = local_address.split(':')[-1]
                ports.append({
                    "port": port,
                    "address": local_address,
                    "state": "LISTEN"
                })
    
    print(f"[+] {len(ports)} ports en écoute détectés")
    return ports

def export_json(data, filename):
    """Exporte les données d'audit au format JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[+] Export JSON : {filename}")


def export_csv(data, filename, fieldnames):
    """Exporte les données d'audit au format CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"[+] Export CSV  : {filename}")

if __name__ == "__main__":
    print("=" * 50)
    print("  AEGIS — Script d'audit de sécurité")
    print(f"  Hôte    : {socket.gethostname()}")
    print(f"  Date    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    services = get_active_services()
    ports    = get_open_ports()

    rapport = {
        "meta": {
            "date": datetime.datetime.now().isoformat(),
            "hostname": socket.gethostname(),
            "auditeur": "Groupe 7"
        },
        "services_actifs": services,
        "ports_ouverts": ports
    }

    os.makedirs("resultats", exist_ok=True)

    export_json(rapport, "resultats/audit_techsud.json")
    export_csv(services, "resultats/services.csv",
               fieldnames=["name", "load", "active", "sub"])
    export_csv(ports, "resultats/ports.csv",
               fieldnames=["port", "address", "state"])

    print("=" * 50)
    print("Audit terminé")
    print("=" * 50)
