from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from datetime import datetime, timedelta

# Generate an ECDSA private key
private_key = ec.generate_private_key(ec.SECP384R1())

# Define the subject and issuer name (self-signed CA)
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "AN"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Anonymous"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Anonymous"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "EmuOCPP-CA"),
    x509.NameAttribute(NameOID.COMMON_NAME, "EmuOCPP-CA"),
])

# Define the certificate
certificate = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=3650))  # 10 years validity
    .add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True  # CA certificate
    )
    .add_extension(
        x509.KeyUsage(
            key_cert_sign=True, crl_sign=True,
            digital_signature=False, key_encipherment=False, content_commitment=False,
            data_encipherment=False, key_agreement=False, encipher_only=False, decipher_only=False
        ), critical=True
    )
    .sign(private_key, hashes.SHA384())  # Secure hashing with SHA-384
)

# Save the private key to a file
with open("emuocpp_ttp_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Save the certificate to a file
with open("emuocpp_ttp_cert.pem", "wb") as f:
    f.write(certificate.public_bytes(serialization.Encoding.PEM))

print("CA Certificate and Key generated successfully!")
