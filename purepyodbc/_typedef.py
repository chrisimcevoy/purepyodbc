"""This module is more or less a transcription of sqltypes.h"""
import ctypes
import ctypes as c


SIZEOF_LONG_INT = c.sizeof(c.c_long)

# Standard SQL data types.
SQLCHAR = c.c_ubyte
SQLDATE = c.c_ubyte
SQLDECIMAL = c.c_ubyte
SQLDOUBLE = c.c_double
SQLFLOAT = c.c_double
SQLINTEGER = c.c_int
SQLUINTEGER = c.c_uint
SQLLEN = c.c_long
SQLULEN = c.c_ulong
SQLSETPOSIROW = c.c_ulong
SQLROWCOUNT = SQLULEN
SQLROWSETSIZE = SQLULEN
SQLTRANSID = SQLULEN
SQLROWOFFSET = SQLULEN
SQLNUMERIC = c.c_byte
SQLPOINTER = c.c_void_p
SQLREAL = c.c_float
SQLSMALLINT = c.c_short
SLQUSMALLINT = c.c_ushort
SQLTIME = c.c_ubyte
SQLTIMESTAMP = c.c_ubyte
SQLVARCHAR = c.c_ubyte
SQLRETURN = SQLSMALLINT
SQLHANDLE = c.c_void_p
SQLHENV = SQLHANDLE
SQLHDBC = SQLHANDLE
SQLHSTMT = SQLHANDLE
SQLHDESC = SQLHANDLE

# More basic data types to augment what windows.h provides
UCHAR = ctypes.c_ubyte
SCHAR = c.c_char
SQLSCHAR = SCHAR
if SIZEOF_LONG_INT == 4:
    SDWORD = c.c_long
    UDWORD = c.c_ulong
else:
    SDWORD = c.c_int
    UDWORD = c.c_uint
SWORD = c.c_short
UWORD = c.c_ushort
UINT = c.c_uint
SLONG = c.c_long
SSHORT = c.c_short
ULONG = c.c_ulong
USHORT = c.c_ushort
SDOUBLE = c.c_double
LDOUBLE = c.c_double
SFLOAT = c.c_float
PTR = c.c_void_p
RETCODE = c.c_short
SQLHWND = c.c_void_p
SQLUSMALLINT = c.c_ushort
