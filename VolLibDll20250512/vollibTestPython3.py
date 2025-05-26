from ctypes import *
#load vollib.dll from your local path
mydll = windll.LoadLibrary(r"C:\development\NVEL\64\vollib.dll")
#*****************************************************************
#-------test the VERNUM routine----------------------------------#
version = c_int()
mydll.VERNUM(byref(version))
print('version = ', version.value)
#*****************************************************************
#this class represents a c style string which has
#the string (str) and an integer length parameter(len)
class fchar(Structure):
  _fields_ = [
				('str', c_char_p),
				('len', c_int),
				 ]
#*****************************************************************
#-------test the GETVOLEQ routine--------------------------------#
#This is to get the NVEL default voleq for a given regn, forst, and species
regn = c_int(9)

forst = fchar()
forst.str = b'01'
forst.len = 2

dist = fchar()
dist.str = b'01'
dist.len = 2
idist = c_int(1)
spec =  c_int(833)

prod = fchar()
prod.str = b'01'
prod.len = 2

voleq = fchar()
voleq.str = b''
voleq.len = 0

errflag = c_int(0)
print('before call GETVOLEQ')
mydll.GETVOLEQ(byref(regn), forst.str,forst.len, dist.str,dist.len, byref(spec), prod.str,prod.len, voleq.str,voleq.len, byref(errflag))

#print('after GETVOLEQ voleq = ', voleq.str)
#*****************************************************************
#-------test the GETVOL routine----------------------------------#
MTOPP = c_float(0)
MTOPS = c_float(0)
STUMP = c_float(0)
DBHOB = c_float(15.1)
DRCOB = c_float(0)
HTTYPE = fchar()
HTTYPE.str = b"F "
HTTYPE.len = 2
HTTOT = c_float(76.4)
HTLOG = c_int()
HT1PRD = c_float(0)
HT2PRD = c_float(0)
UPSHT1 = c_float(0)
UPSHT2 = c_float(0)
UPSD1 = c_float(0)
UPSD2 = c_float(0)
HTREF = c_int(0)
AVGZ1 = c_float(0)
AVGZ2 = c_float(0)
FCLASS = c_int(0)
DBTBH = c_float(0)
BTR = c_float(0)
I3 = c_int(3)
I7 = c_int(7)
I15 = c_int(15)
I20 = c_int(20)
I21 = c_int(21)

REAL = c_float
REAL_P = POINTER(REAL)

VOL = (REAL*15)()

LOGVOL = (REAL*7*20)()

LOGDIA = (REAL*21*3)()

LOGLEN = (REAL*20)()

BOLHT = (REAL*21)()

TLOGS = c_int(0)
NOLOGP = c_float(0)
NOLOGS = c_float(0)
CUTFLG = c_int(1)
BFPFLG = c_int(1)
CUPFLG = c_int(1)
CDPFLG = c_int(1)
CUSFLG = c_int(1)
CDSFLG = c_int(1)
SPFLG = c_int(1)
PROD = fchar()
PROD.str = b"01 "
PROD.len = 3
CONSPEC = fchar()
CONSPEC.str = b"     "
CONSPEC.len = 5
HTTFLL = c_int(0)
LIVE = fchar()
LIVE.str = b"L "
LIVE.len = 2
BA = c_int(0)
SI = c_int(0)
mCTYPE = fchar()
mCTYPE.str = b"F "
mCTYPE.len = 2
ERRFLAG = c_int(0)
idist = c_int(1)
INDEB = c_int(0)
voleq.str = b'900CLKE833'
voleq.len = 10
print('(Input for DLL) voleq = ', voleq.str)
print('(Input for DLL) DBHOB = ', DBHOB.value)
print('(Input for DLL) HTTOT = ', HTTOT.value)
mydll.VOLUMELIBRARY(byref(regn), forst.str,forst.len,voleq.str,voleq.len, byref(MTOPP), byref(MTOPS), byref(STUMP),byref(DBHOB),
byref(DRCOB), HTTYPE.str,HTTYPE.len, byref(HTTOT), byref(HTLOG), byref(HT1PRD), byref(HT2PRD), byref(UPSHT1), byref(UPSHT2), byref(UPSD1),
byref(UPSD2), byref(HTREF), byref(AVGZ1), byref(AVGZ2), byref(FCLASS), byref(DBTBH), byref(BTR), byref(I3), byref(I7), byref(I15), byref(I20), byref(I21),
byref(VOL), byref(LOGVOL), byref(LOGDIA), byref(LOGLEN), byref(BOLHT), byref(TLOGS), byref(NOLOGP), byref(NOLOGS), byref(CUTFLG),
byref(BFPFLG), byref(CUPFLG), byref(CDPFLG), byref(SPFLG), CONSPEC.str,CONSPEC.len,PROD.str, PROD.len, byref(HTTFLL),LIVE.str,LIVE.len,
byref(BA) , byref(SI),mCTYPE.str,mCTYPE.len, byref(ERRFLAG), byref(idist))

print ('ERRFLAG = ', ERRFLAG.value)
for index, item in enumerate(VOL):
	print ('VOL[',index+1,'] = ',item)

print (LOGLEN[0])
print (LOGVOL[0][0])
