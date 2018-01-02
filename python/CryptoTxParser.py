import time
from urllib.request import urlopen
import json
import sys
from datetime import datetime
import optparse
from decimal import *
from dateutil import parser
from time import mktime
from copy import deepcopy

class CryptoCompare(object):
    URL = "https://min-api.cryptocompare.com"
    LIST = "/data/all/coinlist"
    HISTORICAL = "/data/pricehistorical"
    
    def __init__(self):
        self.lastReq = round(mktime(datetime.now().timetuple()))
        self.coins = []
        try:
            with urlopen(CryptoCompare.URL+CryptoCompare.LIST) as d:
                data = json.loads(d.readline())
                if 'Response' in data and data['Response'] == "Success" and 'Data' in data:
                    for key in data['Data']:
                        self.coins.append(key)
                else:
                    raise Exception
        except Exception as e:
            raise Exception

    def getPrice(self, base="", quote="", ts=""):
        if not base or not quote or not ts:
            return None
        if self.lastReq == round(mktime(datetime.now().timetuple())):
            time.sleep(1)
        self.lastReq = round(mktime(datetime.now().timetuple()))
        base = base.upper()
        quote = quote.upper()
        with urlopen(CryptoCompare.URL+CryptoCompare.HISTORICAL+"?fsym="+base+"&tsyms="+quote+"&ts="+ts) as d:
            data = json.loads(d.readline())
            if 'Response' in data and data['Response'] == "Error":
                return None
            if base in data and quote in data[base]:
                return data[base][quote]
            return None
        
    def hasCoin(self, coin):
        for c in self.coins:
            if c.upper() == coin.upper():
                return True
        return False
        
cryptocompare = CryptoCompare()
ltDays = 0
activeYear = -1
debug = False

def unixTs2Date(ts):
    return datetime.fromtimestamp(ts).strftime('%m-%d-%Y %H:%M:%S')
    
def pxFormat(dec, places=8):
    return '{0:.{places}f}'.format(dec, places=places)

class TXLine(object):
    def __init__(self, line):
        lineAr = line.strip().split(',')
        if debug:
            print(lineAr)
        if len(lineAr) < 8:
            raise ValueError
        try:
            self.setTs(lineAr[0])
        except Exception as e:
            print(str(e)+": "+lineAr[0])
            raise e
        self.setType(lineAr[1])
        self.setSrcCurrency(lineAr[2])
        self.setDstCurrency(lineAr[3])
        self.setSrcWallet(lineAr[4])
        self.setDstWallet(lineAr[5])
        self.setSrcValue(lineAr[6])
        self.setDstValue(lineAr[7])
        self.notes = ""
        if len(lineAr) > 8:
            self.setNotes(lineAr[8])
        self.srcFiatValue = Decimal(0)
        
    def setTs(self, ts):
        dt = parser.parse(ts)
        self.ts = round(mktime(dt.timetuple()))

    def setType(self, type):
        if type.lower() == "b" or type.lower() == "buy":
            self.type = "buy"
        elif type.lower() == "s" or type.lower() == "sell":
            self.type = "sell"
        elif type.lower() == "x" or type.lower() == "xfer" or type.lower() == "transfer":
            self.type = "transfer"
        elif type.lower() == "o" or type.lower() == "out" or type.lower() == "outbound":
            self.type = "outbound"
        elif type.lower() == "i" or type.lower() == "in" or type.lower() == "inbound":
            self.type = "inbound"
        else:
            self.type = "unknown"        

    def setSrcCurrency(self, srcCurrency):
        self.srcCurrency = srcCurrency

    def setDstCurrency(self, dstCurrency):
        self.dstCurrency = dstCurrency

    def setSrcWallet(self, srcWallet):
        self.srcWallet = srcWallet

    def setDstWallet(self, dstWallet):
        self.dstWallet = dstWallet

    def setSrcValue(self, srcValue):
        self.srcValue = Decimal(srcValue)

    def setDstValue(self, dstValue):
        self.dstValue = Decimal(dstValue)
        
    def setSrcFiatValue(self, srcFiatValue, srcValue):
        self.srcFiatValue = Decimal(srcFiatValue) * Decimal(srcValue)

    def setNotes(self, notes):
        self.notes = notes

    def __str__(self):
        s = ""
        s += "   timestamp:              "+unixTs2Date(self.ts)+" ("+str(self.ts)+")\n"
        s += "   transaction type:       "+self.type+"\n"
        s += "   source currency:        "+self.srcCurrency+"\n"
        s += "   destination currency:   "+self.dstCurrency+"\n"
        s += "   source wallet:          "+self.srcWallet+"\n"
        s += "   destination wallet:     "+self.dstWallet+"\n"
        s += "   source value:           "+pxFormat(self.srcValue)+"\n"
        s += "   destination value:      "+pxFormat(self.dstValue)+"\n"
        if self.srcFiatValue != Decimal(0):
            s += "   source fiat value:      "+pxFormat(self.srcFiatValue)+"\n"
        s += "   notes:                  "+str(self.notes)+"\n"
        return s
        
class Record(object):
    def __init__(self, ts, coinVal = Decimal(0), fiatVal = Decimal(0), gain = Decimal(0), originalTs = 0):
        self.ts = ts
        self.originalTs = originalTs
        self.coinVal = coinVal
        self.fiatVal = fiatVal
        self.gain = gain
            
    def setFiatVal(self, currency, fiat):
        fiatPx = Decimal(cryptocompare.getPrice(base=currency, quote=fiat, ts=str(ts)))
        self.fiatVal = fiatPx * self.coinVal
        
    def isShortTerm(self):
        if self.originalTs == 0:
            return True
        if (datetime.fromtimestamp(self.ts) - datetime.fromtimestamp(self.originalTs)).days > ltDays:
            return False
        return True
            
    def __str__(self):
        s = ""
        s += " Timestamp ........... "+unixTs2Date(self.ts)+" ("+str(self.ts)+")\n"
        if self.originalTs != 0:
            s += " Original Timestamp .. "+unixTs2Date(self.originalTs)+" ("+str(self.originalTs)+")\n"
        s += " Coin Value .......... "+pxFormat(self.coinVal)+"\n"
        s += " Fiat Value .......... "+pxFormat(self.fiatVal, places=2)+"\n"
        s += " Gain ................ "+pxFormat(self.gain, places=2)+"\n"
        if self.gain != Decimal(0):
            s += " Gain Type ........... "+("short term" if self.isShortTerm() else "long term")+"\n"
        s += "\n"
        return s
        
class FiatWallet(object):
    def __init__(self, fiatCurrency):
        self.fiatCurrency = fiatCurrency
        self.txs = []
        self.bal = Decimal(0)
        self.netGains = Decimal(0)
        self.stRecs = []
        self.stGains = Decimal(0)
        self.ltRecs = []
        self.ltGains = Decimal(0)
        
    def add(self, txInfo, recs):
        self.txs.append(deepcopy(txInfo))
        for rec in recs:
            self.bal += rec.fiatVal
            if activeYear == -1 or activeYear == datetime.fromtimestamp(rec.ts).year:
                self.netGains += rec.gain
                if rec.isShortTerm():
                    self.stRecs.append(deepcopy(rec))
                    self.stGains += rec.gain
                else:
                    self.ltRecs.append(deepcopy(rec))
                    self.ltGains += rec.gain
        
    def rem(self, txInfo, rec):
        self.txs.append(deepcopy(txInfo))
        newRec = deepcopy(rec)
        newRec.fiatVal = newRec.fiatVal * Decimal(-1)
        self.bal = self.bal + newRec.fiatVal
    
    def __str__(self):
        s = "Fiat Wallet Info:\n"
        s += "Fiat Currency ... "+self.fiatCurrency+"\n"
        s += "Related Transactions:\n"
        for tx in self.txs:
            s += str(tx)+"\n"
        s += "Balance: "+pxFormat(self.bal, places=2)+"\n"
        s += self.getGainSummary()
        return s
    
    def getGainSummary(self):
        s = "Gain Summary for "+("all years" if activeYear == -1 else "year "+str(activeYear))+"\n"
        s += "Net Gain: "+pxFormat(self.netGains, places=2)+"\n"
        s += "\n"
        s += "## Long-term gain records ##\n"
        for rec in self.ltRecs:
            s += str(rec)
        s += "Long-term gains ...... "+pxFormat(self.ltGains, places=2)+"\n"
        s += "\n"
        s += "## Short-term gain records ##\n"
        for rec in self.stRecs:
            s += str(rec)
        s += "Short-term gains ..... "+pxFormat(self.stGains, places=2)+"\n"
        s += "\n"
        return s

class Wallet(object):
    def __init__(self, name):
        self.name = name
        self.coins = {}
            
    def __str__(self):
        s = "Wallet Info:\n"
        s += "Wallet Name ... "+self.name+"\n"
        for key in self.coins:
            s += str(self.coins[key])+"\n"
        return s
    
class Coin(object):
    def __init__(self, name):
        self.name = name
        self.txs = []
        self.curRecs = []
        
    def add(self, txInfo, recs):
        for rec in recs:
            self.txs.append(deepcopy(txInfo))
            self.curRecs.append(deepcopy(rec))            
        
    def rem(self, txInfo, recs, xfer=False):
        if debug:
            print("<< current records before removal")
            for curRec in self.curRecs:
                print(str(curRec)+"\n")
            print(">> current records before removal")
        self.txs.append(deepcopy(txInfo))
        retRecs = []
        for rec in recs:
            for curRec in self.curRecs:
                if rec.coinVal != Decimal(0):
                    if rec.coinVal >= curRec.coinVal:
                        pct = curRec.coinVal / rec.coinVal
                        curRecFiatVal = curRec.fiatVal
                        recFiatVal = (rec.fiatVal * pct)
                        rec.coinVal = rec.coinVal - curRec.coinVal
                        rec.fiatVal = rec.fiatVal - recFiatVal
                        originalTs = curRec.originalTs
                        if originalTs == 0:
                            originalTs = curRec.ts  
                        tmpRec = Record(rec.ts, coinVal = curRec.coinVal, fiatVal = curRecFiatVal if xfer else recFiatVal, gain = (recFiatVal - curRecFiatVal) if not xfer else rec.gain, originalTs = originalTs)
                        retRecs.append(tmpRec)
                        curRec.coinVal = Decimal(0)
                    else:
                        pct = rec.coinVal / curRec.coinVal
                        curRecFiatVal = (curRec.fiatVal * pct)
                        recFiatVal = (rec.fiatVal * pct)
                        curRec.coinVal = curRec.coinVal - rec.coinVal
                        curRec.fiatVal = curRec.fiatVal - curRecFiatVal
                        originalTs = curRec.originalTs
                        if originalTs == 0:
                            originalTs = curRec.ts  
                        tmpRec = Record(rec.ts, coinVal = rec.coinVal, fiatVal = curRecFiatVal if xfer else recFiatVal, gain = (rec.fiatVal - curRecFiatVal) if not xfer else rec.gain, originalTs = originalTs)
                        retRecs.append(tmpRec)
                        rec.coinVal = Decimal(0)
        self.curRecs = [i for i in self.curRecs if not i.coinVal.is_zero()]
        if debug:
            print("<< current records after removal")
            for curRec in self.curRecs:
                print(str(curRec)+"\n")
            print(">> current records after removal")
            print("<< records we removed")
            for rec in retRecs:
                print(str(rec)+"\n")
            print(">> records we removed")
        return retRecs
    
    def __str__(self):
        s = ""
        s += "Currency Name ... "+self.name+"\n"
        s += "Related Transactions:\n"
        for tx in self.txs:
            s += str(tx)+"\n"
        bal = Decimal(0)
        for curRec in self.curRecs:
            bal += curRec.coinVal
        s += "Balance: "+pxFormat(bal)+"\n"
        return s
    
def getWallet(wallets, name):
    if name not in wallets:
        wallets[name] = Wallet(name)
    return wallets[name]
    
def getCoin(wallet, coin):
    if coin not in wallet.coins:
        wallet.coins[coin] = Coin(coin)
    return wallet.coins[coin]
            
def processTransaction(wallets, fiatWallet, txInfo):
    if debug:
        print("****************************************")
        print("<< current transaction being processed")
        print(txInfo)
        print(">> current transaction being processed")
    if txInfo.srcCurrency == fiatWallet.fiatCurrency and txInfo.dstCurrency == fiatWallet.fiatCurrency:
        return
    if txInfo.srcCurrency == fiatWallet.fiatCurrency:
        #we are converting from fiat, so remove from fiat wallet, add coins to wallet
        if debug:
            print("1 we are converting from fiat, so remove from fiat wallet, add coins to wallet")
        rec1 = Record(txInfo.ts, fiatVal = txInfo.srcValue)
        fiatWallet.rem(txInfo, rec1)
        wallet = getWallet(wallets, txInfo.dstWallet)
        coin = getCoin(wallet, txInfo.dstCurrency)
        rec2 = Record(txInfo.ts, coinVal = txInfo.dstValue, fiatVal = txInfo.srcValue)
        coin.add(txInfo, [rec2])
    elif txInfo.dstCurrency == fiatWallet.fiatCurrency:
        #we are converting into fiat, so add to fiat wallet, remove coins from wallet
        if debug:
            print("2 we are converting into fiat, so add to fiat wallet, remove coins from wallet")
        wallet = getWallet(wallets, txInfo.srcWallet)
        coin = getCoin(wallet, txInfo.srcCurrency)
        rec1 = Record(txInfo.ts, coinVal = txInfo.srcValue, fiatVal = txInfo.dstValue)
        recs = coin.rem(txInfo, [rec1])
        fiatWallet.add(txInfo, recs)
    else:
        if txInfo.srcCurrency == txInfo.dstCurrency:
            #we are not converting from fiat- this is a transfer
            if debug:
                print("3a we are not converting from fiat- this is a transfer")
            if txInfo.type == "outbound":
                #payment out, so calculate tax gains
                if debug:
                    print("3a1 payment out, so calculate tax gains")
                wallet = getWallet(wallets, txInfo.srcWallet)
                coin = getCoin(wallet, txInfo.srcCurrency)
                rec1 = Record(txInfo.ts, coinVal = txInfo.srcValue, fiatVal = (Decimal(cryptocompare.getPrice(base=txInfo.srcCurrency, quote=fiatWallet.fiatCurrency, ts=str(txInfo.ts))) * txInfo.srcValue))
                recs = coin.rem(txInfo, [rec1])
                fiatWallet.add(txInfo, recs)
            elif txInfo.type == "transfer":
                #transfer coins from wallet to wallet
                if debug:
                    print("3a2 transfer coins from wallet to wallet")
                wallet = getWallet(wallets, txInfo.srcWallet)
                coin = getCoin(wallet, txInfo.srcCurrency)
                rec1 = Record(txInfo.ts, coinVal = txInfo.srcValue)
                recs = coin.rem(txInfo, [rec1], xfer=True)
                #distribute fees
                fees = txInfo.srcValue - txInfo.dstValue
                for rec in reversed(recs):
                    if fees <= rec.coinVal:
                        rec.coinVal -= fees
                    else:
                        rmvd = rec.coinVal
                        rec.coinVal = Decimal(0)
                        fees -= rmvd                
                wallet = getWallet(wallets, txInfo.dstWallet)
                coin = getCoin(wallet, txInfo.dstCurrency)
                coin.add(txInfo, recs)
            elif txInfo.type == "inbound":
                #someone paid us, so calculate as 100% gains
                if debug:
                    print("3a3 someone paid us, so calculate as 100% gains")
                rec1 = Record(txInfo.ts, coinVal = txInfo.dstValue, fiatVal = (Decimal(cryptocompare.getPrice(base=txInfo.dstCurrency, quote=fiatWallet.fiatCurrency, ts=str(txInfo.ts))) * txInfo.dstValue))
                wallet = getWallet(wallets, txInfo.dstWallet)
                coin = getCoin(wallet, txInfo.dstCurrency)
                coin.add(txInfo, [rec1])
                fiatWallet.add(txInfo, [rec1])
            else:
                print("unknown transaction type:"+txInfo.type)
                return
        else:
            #we are not converting from fiat- not a transfer- we are converting coin to coin
            if debug:
                print("3b we are not converting from fiat- not a transfer- we are converting coin to coin")
            wallet = getWallet(wallets, txInfo.srcWallet)
            coin = getCoin(wallet, txInfo.srcCurrency)
            rec1 = Record(txInfo.ts, coinVal = txInfo.srcValue, fiatVal = (Decimal(cryptocompare.getPrice(base=txInfo.srcCurrency, quote=fiatWallet.fiatCurrency, ts=str(txInfo.ts))) * txInfo.srcValue))
            recs = coin.rem(txInfo, [rec1])
            fiatWallet.add(txInfo, recs)
            wallet = getWallet(wallets, txInfo.dstWallet)
            coin = getCoin(wallet, txInfo.dstCurrency)
            rec2 = Record(txInfo.ts, coinVal = txInfo.dstValue, fiatVal = (Decimal(cryptocompare.getPrice(base=txInfo.dstCurrency, quote=fiatWallet.fiatCurrency, ts=str(txInfo.ts))) * txInfo.dstValue))
            coin.add(txInfo, [rec2])
    if debug:
        print("****************************************")
    
def parseFile(fiatCurrency, fn, printSummary, ignoreHeader=True):
    try:
        api = CryptoCompare()
    except Exception as e:
        raise Exception
    txs = []
    errors = []
    with open(fn, 'r') as f:
        for line in f:
            if ignoreHeader:
                ignoreHeader = False
                continue
            line = line.strip()
            if len(line) == 0:
                continue
            try:
                tx = TXLine(line)
                txs.append(tx)
            except Exception as e:
                errors.append(line)
    if len(errors) > 0:
        print("The following lines had errors. Please check your data")
        for e in errors:
            print(e)
        return
        
    fiatWallet = FiatWallet(fiatCurrency)
    coinWallets = {}
    
    txs.sort(key=lambda tx: tx.ts)
    
    for tx in txs:
        if tx.type == "payment" or tx.type == "transfer":
            if tx.srcCurrency == "" and srcCurrency == "":
                continue
            elif tx.dstCurrency == "" and tx.srcCurrency != "":
                tx.dstCurrency = tx.srcCurrency
            elif tx.srcCurrency == "" and tx.dstCurrency != "":
                tx.srcCurrency = tx.dstCurrency
            else:
                tx.srcCurrency = tx.dstCurrency
        processTransaction(coinWallets, fiatWallet, tx)
    
    if printSummary:
        for key in coinWallets:
            print(str(coinWallets[key]))
    print(fiatWallet.getGainSummary())
    
def main():
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', dest='file', help='file with transaction logs')
    parser.add_option('-c', '--fiat_currency', dest='fiatCurrency', default="USD", help='base fiat currency to use')
    parser.add_option('-l', '--long_term_days', dest='ltDays', default=366, help='days until considered long term gain, default=366 (add one for leap-year safety)')
    parser.add_option('-y', '--year', dest='year', default=-1, help='year to evaluate gains for, -1 (default) for all transactions')
    parser.add_option('-s', '--summary', dest='summary', action="store_true", default=False, help='print wallet summaries')
    parser.add_option('-H', '--no_header', dest='no_header', action="store_true", default=False, help='if your data does not have a header, turn this flag on')
    parser.add_option('-D', '--debug', dest='debug', action="store_true", default=False, help='enable debugging')

    (options, args) = parser.parse_args()

    if not options.file:
        print("no file specified")
        parser.print_help()
        sys.exit(1)

    global ltDays
    ltDays = options.ltDays
    
    global activeYear
    activeYear = int(options.year)
    
    global debug
    debug = options.debug
    
    try:
        parseFile(options.fiatCurrency, options.file, options.summary, ignoreHeader=(False if options.no_header else True))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
