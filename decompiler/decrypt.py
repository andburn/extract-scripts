#!/usr/bin/env python

import binascii
import sys
import blowfish

# DOS Header
DOS_PE_OFFSET = 0x3C # Field containing the PE header offset
DOS_PE_LENGTH = 0x4 # The offset is encoded within 4 bytes (little-endian)

# Standard PE header (consists of the PE signature and COFF header)
PE_SIGN_LENGTH = 0x4 # PE Signature is encoded within 4 bytes
COFF_HEADER_SIZE = 0x14 # Size of all fields within COFF header

# PE-Optional header
PE_OPT_SIGN_LENGTH = 0x2 # Signature encoded within 2 bytes (exact)
PE_OPT_SIGN_32 = 0x010B # Signature for 32 bit executable
PE_OPT_SIGN_64 = 0x020B # Signature for 64 bit executable
# !! The structure of the PE OPT header is different for x32 and x64
# The following two fields hold the size of the entire PE header (incl DOS stub)
PE_OPT_32_HSIZE_OFFSET = 0x3C
PE_OPT_64_HSIZE_OFFSET = 0x3C
PE_OPT_X_HSIZE_LENGTH = 0x4 # On both architectures encoded within 2 bytes (little-endian)

def get_pe_offset(buf):
	pe_offset_bytes = buf[DOS_PE_OFFSET: DOS_PE_OFFSET+DOS_PE_LENGTH]
	return int.from_bytes(pe_offset_bytes, 'little')

def get_total_header_size(buf, pe_offset):
	# Skip STD-PE header, into PE-OPT header
	offset = pe_offset + PE_SIGN_LENGTH + COFF_HEADER_SIZE
	
	# Detect file target architecture
	arch_bytes = buf[offset: offset+PE_OPT_SIGN_LENGTH]
	arch = int.from_bytes(arch_bytes, 'little')
	# Add the architecture specific offset towards the header field.
	# The added offset counts from the beginning of the PE-OPT structure.
	if arch == PE_OPT_SIGN_32:
		offset += PE_OPT_32_HSIZE_OFFSET
	elif arch == PE_OPT_SIGN_64:
		offset += PE_OPT_64_HSIZE_OFFSET
	else:
		raise ValueError('Unknown architecture!')

	header_size_bytes = buf[offset:offset+PE_OPT_X_HSIZE_LENGTH]
	return int.from_bytes(header_size_bytes, 'little')

def decrypt(input_file, output_file):
	with open(input_file, "rb") as f:
		buf = f.read()

	# The PE signature is the first field of the STD-PE header
	pe_sign_offset = get_pe_offset(buf)
	pe_sign = buf[pe_sign_offset: pe_sign_offset+PE_SIGN_LENGTH]
	if pe_sign == b"PE\0\0":
		print("File is not encrypted")
		write_decrypted_output(buf, pe_sign_offset, output_file)
		return False

	header_size = get_total_header_size(buf, pe_sign_offset)
	print("Header size: 0x{:02X}".format(header_size))

	print("Decrypting %r" % (input_file))
	key_offset = len(buf) - 0x38 - 5
	key = buf[key_offset:-5]
	print("Key:", binascii.hexlify(key))

	encrypted = buf[header_size:key_offset]

	cipher = blowfish.Cipher(key)
	decrypted = b"".join(cipher.decrypt_ecb(encrypted))
	clear_header = buf[:header_size]

	write_decrypted_output(clear_header + decrypted, pe_sign_offset, output_file)

	return True


def write_decrypted_output(output, pe_sign_offset, output_file):
	with open(output_file, "wb") as f:
		f.write(output)

		f.seek(pe_sign_offset)
		f.write(b"PE\0\0")

	print("Written to %r" % (output_file))


def main():
	decrypt(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
	main()
