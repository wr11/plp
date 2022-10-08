'''import struct
res=struct.pack("i", 1)
res2=struct.pack("4s", b"good")
u = struct.unpack("i", res2)
PrintDebug(res2, type(res2))
PrintDebug(u, type(u))'''

'''import msgpack
msg = msgpack.pack({1:2,"name":"arr"})
msg2=msgpack.unpack(msg)
PrintDebug(msg)
PrintDebug(msg2)'''

# import  struct
# import binascii
# import ctypes
# import msgpack

# msg = msgpack.packb({1:2,"name":"arr"})
# PrintDebug(msg)
 
'''values = (1, b'good' , 1.22) #查看格式化字符串可知，字符串必须为字节流类型。
s =  struct .Struct( 'I4sf' )
buff = ctypes.create_string_buffer(s.size)
packed_data = s.pack_into(buff,0,*values)
unpacked_data = s.unpack_from(buff,0)
  
PrintDebug( 'Original values:' , values)
PrintDebug( 'Format string :' , s.format)
PrintDebug( 'buff :' , buff)
PrintDebug( 'Packed Value :' , binascii.hexlify(buff))
PrintDebug( 'Unpacked Type :' , type(unpacked_data),  ' Value:' , unpacked_data)'''

def Print(*args):
	print(args, *args)
	args = [str(i) for i in args]
	sMsg = "Print%s"%(" ".join(args))
	print(sMsg)

def K():
	Print(1)
	Print("s")
	Print((1,2))
	Print([1,3])
	Print({1,5})
	try:
		a-b
	except Exception as e:
		Print(e)