import bcrypt


def hash_password(plain: str) -> str:
    # gensalt stvara novi nasumični salt i upisuje ga u rezultat,
    # zajedno s oznakom algoritma i faktorom rada
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    # checkpw iz zapisa iščita salt i faktor rada, ponovi izračun i usporedi
    return bcrypt.checkpw(plain.encode(), hashed.encode())
