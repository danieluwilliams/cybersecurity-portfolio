import ipaddress
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_ca_certificate():
    """Generate the Certificate Authority (CA) certificate."""

    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    ca_name = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Grand Marina Hotel"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Water Systems Security"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Grand Marina Root CA"),
    ])

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return ca_key, ca_cert


def generate_server_certificate(ca_key, ca_cert):
    """Generate the server certificate signed by the CA."""

    server_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    server_name = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Grand Marina Hotel"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "MQTT Broker"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_name)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return server_cert, server_key


def save_certificates(ca_cert, server_cert, server_key, output_dir="certs"):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    with open(output_path / "ca.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    with open(output_path / "server.pem", "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))

    with open(output_path / "server-key.pem", "wb") as f:
        f.write(server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))


if __name__ == "__main__":
    ca_key, ca_cert = generate_ca_certificate()
    server_cert, server_key = generate_server_certificate(ca_key, ca_cert)
    save_certificates(ca_cert, server_cert, server_key)
    print("Certificates generated in ./certs")
