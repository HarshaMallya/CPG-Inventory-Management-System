import bcrypt

def hash_password(password):
    """Generate bcrypt hash for password"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

if __name__ == "__main__":
    passwords = {
        "admin123": hash_password("admin123"),
        "manager123": hash_password("manager123"),
        "employee123": hash_password("employee123")
    }
    
    print("Generated Password Hashes:")
    print("=" * 80)
    for pwd, hash_val in passwords.items():
        print(f"\nPassword: {pwd}")
        print(f"Hash: {hash_val}")
    print("\n" + "=" * 80)
    print("\nCopy these hashes to config.yaml")
