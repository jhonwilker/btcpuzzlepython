import hashlib
import binascii
def private_key_to_wif(private_key):
    extended_key = '80' + private_key
    first_sha256 = hashlib.sha256(binascii.unhexlify(extended_key)).hexdigest()
    second_sha256 = hashlib.sha256(binascii.unhexlify(first_sha256)).hexdigest()
    checksum = second_sha256[:8]
    final_key = extended_key + checksum
    final_key_bytes = binascii.unhexlify(final_key)
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    value = int.from_bytes(final_key_bytes, 'big')
    result = ''
    while value > 0:
        value, mod = divmod(value, 58)
        result = alphabet[mod] + result
    pad = 0
    for byte in final_key_bytes:
        if byte == 0:
            pad += 1
        else:
            break
    return alphabet[0] * pad + result
private_key = input("Digite a chave privada em formato hexadecimal: ")
wif = private_key_to_wif(private_key)
print("WIF:", wif)
with open("output.txt", "w") as file:
    file.write("Chave WIF: " + wif + "\n")