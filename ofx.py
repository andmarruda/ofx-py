import os
import re
from bs4 import BeautifulSoup
import datetime

class ofx:
    def __init__(self, file):
        if not(os.path.isfile(file)):
            raise Exception('Path for OFX file doesn\`t exists.')
        self._properties = {}
        self._xml = '';
        self._workOfx(file)

    def _workOfx(self, file):
        ofx_line = -1
        with open(file) as file:
            for i, line in enumerate(file):
                line = line.strip()
                if re.search(r'^<OFX>$', line):
                    ofx_line=i

                if ofx_line==-1 and re.search(r'^(?!\<)(.*\:)', line) != None:
                    attr = line.split(':')
                    self._properties[attr[0]] = attr[1] or None
                    continue

                self._xml += line

            self._xml = BeautifulSoup(self._xml, 'html.parser')

    def getProperties(self):
        return self._properties

    def signonmsgsrsv1(self):
        sonrs = self._xml.signonmsgsrsv1.sonrs

        return {
            'status_code': sonrs.status.code.string,
            'status_severity': sonrs.status.severity.string,
            'dtserver': datetime.date(int(sonrs.dtserver.string[0:4]), int(sonrs.dtserver.string[4:6]), int(sonrs.dtserver.string[6:8])),
            'language': sonrs.language.string,
            'fi_org': sonrs.fi.org.string,
            'fi_fid': sonrs.fi.fid.string
        }

    def stmttrnrs(self):
        stmttrnrs = self._xml.bankmsgsrsv1.stmttrnrs
        return {
            'trnuid': stmttrnrs.trnuid.string,
            'status_code': stmttrnrs.status.code.string,
            'status_severity': stmttrnrs.status.severity.string
        }

    def account(self):
        stmtrs = self._xml.bankmsgsrsv1.stmttrnrs.stmtrs

        return {
            'currency': stmtrs.curdef.string,
            'bankid': stmtrs.bankacctfrom.bankid.string,
            'branchid': stmtrs.bankacctfrom.branchid.string,
            'acctid': stmtrs.bankacctfrom.acctid.string,
            'accttype': stmtrs.bankacctfrom.accttype.string
        }

    def movements(self):
        banktranlist = self._xml.bankmsgsrsv1.stmttrnrs.stmtrs.banktranlist
        movements = []
        for stmttrn in banktranlist.find_all('stmttrn'):
            movements.append({
                'trntype': stmttrn.trntype.string,
                'dtposted': datetime.date(int(stmttrn.dtposted.string[0:4]), int(stmttrn.dtposted.string[4:6]), int(stmttrn.dtposted.string[6:8])),
                'trnamt': float(stmttrn.trnamt.string),
                'fitid': stmttrn.fitid.string,
                'checknum': stmttrn.checknum.string,
                'refnum': stmttrn.refnum.string,
                'memo': stmttrn.memo.string
            })

        return {
            'dtstart': datetime.date(int(banktranlist.dtstart.string[0:4]), int(banktranlist.dtstart.string[4:6]), int(banktranlist.dtstart.string[6:8])),
            'dtend': datetime.date(int(banktranlist.dtend.string[0:4]), int(banktranlist.dtend.string[4:6]), int(banktranlist.dtend.string[6:8])),
            'movements': movements
        }

o = ofx('./example.ofx')
print(o.getProperties())
print(o.signonmsgsrsv1())
print(o.stmttrnrs())
print(o.account())
print(o.movements())
