#sha256 encryption is used
def encrypt(string):
    bitString = ''
    for char in string:
        bitString+=bin(ord(char)).replace('0b','')
    originalBitStr = bin(len(bitString)).replace('0b','')
    lenOfBitStrofLenOfOriginalBitStr = len(originalBitStr)
    while len(bitString)%512!=512-lenOfBitStrofLenOfOriginalBitStr:
        bitString+='0'
    bitString+=originalBitStr
    



#print(encrypt("hello world"))