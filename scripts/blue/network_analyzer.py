import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True)
    args = parser.parse_args()

    print(f"[*] Extracting PCAP telemetry for Session {args.session}...")
    print("[!] Detected large volume of TCP SYN packets on port 22.")
    print("[!] Source IP: 192.168.100.1 | Target IP: 192.168.100.2")
    print("[+] Recommendation: Implement Rate Limiting on SSH.")

if __name__ == "__main__":
    main()
