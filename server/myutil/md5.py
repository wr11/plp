import random
import hashlib

def GenerateSeed(lstData):
	res = 0
	for seed in lstData:
		sMd5Hash = hashlib.md5(str(seed).encode("utf-8"))
		seed_md5 = int(sMd5Hash.hexdigest(), 16)
		res ^= seed_md5
	return res

def Shuffle(lst, iSeed):
	assert iSeed
	random.seed(iSeed)
	random.shuffle(lst)
	PrintDebug(f"Shuffle Res:{list(i[1] for i in lst)}")

# if __name__ == "__main__":
# 	lstMember = [(51872,"蛋仔"),(93903,"瑜瑾")]
# 	lstSeed = ["56","5896512"]
# 	iSeed = GenerateSeed(lstSeed)
# 	PrintDebug(iSeed)
# 	Shuffle(lstMember, iSeed)