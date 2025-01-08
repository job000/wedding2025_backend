from werkzeug.security import generate_password_hash

new_password = "ossto"
password_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=32)

print(password_hash)
