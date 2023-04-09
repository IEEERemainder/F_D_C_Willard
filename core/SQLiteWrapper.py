import sqlite3
import re
from core.Errors import *
from core.SafeQueryConf import *

safeQueryConfDefault = SafeQueryConf(
    ["Delete","Destroy","AutoCommit","DropIndex","DropTrigger","DropTable","Clear",
    "IncrVacuum","Insert","JournalMode","MakeRecord","Param","Program","PureFunc",
    "SqlExec","Vacuum","ParseSchema"],
    
    ["date","time","datetime","julianday","strftime","acos","acosh","asin","asinh",
    "atan","atan2","atanh","ceil","ceiling","cos","cosh","degrees","exp","floor",
    "ln","log","log10","log2","mod","pi","pow","power","radians","sin","sinh","sqrt",
    "tan","tanh","trunc","json","json_array","json_array_length","json_extract",
    "json_insert","json_object","json_patch","json_remove","json_replace","json_set",
    "json_type","json_valid","json_quote","json_group_array","json_group_object",
    "json_each","json_tree","abs","changes","char","coalesce","glob","hex","ifnull",
    "iif","instr","last_insert_rowid","length","like","likelihood","likely","lower",
    "ltrim","max","min","nullif","quote","random","replace","round","rtrim","sign",
    "soundex","substr","substring","total_changes","trim","typeof","unicode",
    "unlikely","upper"]
)

class SQLiteWrapper:
    def __init__(self, path, allowSQM=False):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        self.safeQueryConf=safeQueryConfDefault
        self.allowSQM = allowSQM

    def exe(self, query, params=[]):
        self.cursor.execute(query, params)
        return self.cursor

    def exefn(self, query, params, fn):
        self.exe(query, params)
        return fn(self.cursor)

    def exep(self, query, params, func):
        return self.exefn(query, params, lambda c: [func(x) for x in c])

    def commit(self):
        self.connection.commit()
    
    def onlyValue(self, query, params=[]):
        return self.exefn(query, params, lambda c: c.fetchone()[0]) 
    
    def onlyInt(self, query, params=[]):
        return int(self.onlyValue(query, params))
    
    def all(self, query, params=[]):
        return self.exefn(query, params, lambda c: c.fetchall())
    
    def exefns(self, func, query, params=[]):
        if not self.allowSQM:
            raise AccessError("Database is not configured to allow orbitrary queries")

        while True: # TODO: is fictive loop needed?
            if re.match("^EXPLAIN", q, re.I):
                break
            if not re.match("^QUERY\s+PLAN", q, re.I):
                equery = "EXPLAIN " + query
            else:
                equery = query
            e = None
            try:
                e = self.all(equery)
            except Exception as e:
                raise InternalError(str(e)) 
            self.safeQueryConf.check(e)
            break
            
        return self.exefn(query, params, func)
