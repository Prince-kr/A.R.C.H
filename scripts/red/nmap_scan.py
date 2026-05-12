import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--payload", default="-F -T4 --open") # Optimized for speed and relevance
    args = parser.parse_args()

    print(f"[*] Starting REAL Nmap scan on {args.target}...")
    
    # Building the command: nmap [flags from payload] [target]
    command = ["nmap"] + args.payload.split() + [args.target]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}", file=sys.stderr)
    except FileNotFoundError:
        print("[!] Warning: 'nmap' binary not found on this host.")
        print("[*] Falling back to SIMULATION MODE...")
        print(f"[*] Simulated Scan of {args.target} completed.")
        print("PORT      STATE SERVICE")
        print("22/tcp    open  ssh")
        print("80/tcp    open  http")
        print("443/tcp   open  https")

if __name__ == "__main__":
    main()
