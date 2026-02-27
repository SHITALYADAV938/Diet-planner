import joblib, os, pprint

# Resolve models path relative to this script
base_dir = os.path.dirname(os.path.abspath(__file__))
enc_path = os.path.join(base_dir, '..', 'models', 'encoders.joblib')
enc_path = os.path.normpath(enc_path)

if not os.path.exists(enc_path):
    print('Encoders file not found at', enc_path)
    raise SystemExit(1)

enc = joblib.load(enc_path)
for k, v in enc.items():
    print('---', k)
    try:
        print(getattr(v, 'classes_', repr(v)))
    except Exception as e:
        print('Type:', type(v), 'repr:', repr(v))
