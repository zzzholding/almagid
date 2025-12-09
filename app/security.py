from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd.verify(plain, hashed)

def hash_password(plain):
    return pwd.hash(plain)
