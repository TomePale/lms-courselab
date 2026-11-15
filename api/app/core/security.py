import bcrypt


def hash_password(plain: str) -> str:
    # gensalt stvara novi nasumični salt i upisuje ga u rezultat,
    # zajedno s oznakom algoritma i faktorom rada
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    data = plain.encode()
    # bcrypt odbija lozinke dulje od 72 bajta (baca ValueError, što bi bila 500).
    # Takva lozinka ne može biti ispravna, jer je pri stvaranju ne dopuštamo.
    if len(data) > 72:
        return False
    # checkpw iz zapisa iščita salt i faktor rada, ponovi izračun i usporedi
    return bcrypt.checkpw(data, hashed.encode())
