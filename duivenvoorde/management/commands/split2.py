'''
split excel spreadsheet into ellitrack datafiles
'''
import xlrd
import re
import os
from xlrd.xldate import xldate_as_datetime

src='/media/sf_C_DRIVE/Users/theo/Documents/projdirs/duivenvoorde/oudedata/tauw/Copy of Voorschoten waterstanden.xlsx'
dest=os.path.dirname(src)

book = xlrd.open_workbook(src) 
sheet=book.sheet_by_name('Blad1')
pattern = re.compile(r'\((\d+)\)')
nrows = sheet.nrows
for pb in range(0,19):
    col = pb * 6
    name = sheet.cell(0,col).value
    match = pattern.search(name)
    serial = match.group(1) if match else '00000000'
    peilbuis = name.split(' ')[1]
    print(peilbuis, serial)
    with open(os.path.join(dest,'Ellitrack-'+serial+'-pb'+peilbuis+'.txt'),'w') as f:
        f.write('Datum\tWaterstand\tTemperatuur water\tTemperatuur intern\n')
        for row in range(2,sheet.nrows):
            try:
                date = xldate_as_datetime(sheet.cell(row,col).value,book.datemode)
                level = sheet.cell(row,col+1).value
                temp1 = sheet.cell(row,col+2).value
                temp2 = sheet.cell(row,col+3).value
                f.write('\t'.join(map(str,[date.strftime('%Y-%m-%d %H:%M:%S'),level,temp1,temp2]))+'\n')
            except:
                break
        