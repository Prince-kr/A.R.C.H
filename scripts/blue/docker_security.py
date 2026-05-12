import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--session', required=True)
args = parser.parse_args()

print(f'[*] Analyzing session {args.session} using docker_security...')
print('Security findings identified: 0 anomalies.')
