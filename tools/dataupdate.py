# -*- coding:utf-8 -*-

import csv
import datetime

def deal_sale_repeat_data(filename, col=None):

    """deal repeat data"""
    startTime = datetime.datetime.now()
    print "开始处理..."
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        o = open('deal'+filename, 'wb')
        writer = csv.writer(o)
        pre_name = ''
        pre_product_id = ''
        pre_date_order = ''

        for line in reader:
            if not line[0]:
                continue
            if reader.line_num == 1:
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip(), line[3].strip(), line[4].strip(), line[5].strip(), line[6].strip(), ])
                continue
            if reader.line_num == 2:
                pre_name = line[0].strip()
                pre_product_id = line[1].strip()
                pre_date_order = line[2].strip()
                print pre_name, pre_product_id, pre_date_order
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip()+' 00:00:00', line[3].strip(), line[4].strip(), line[5].strip(), line[6].strip(), ])
                continue
            if pre_name!=line[0].strip():
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip()+' 00:00:00', line[3].strip(), line[4].strip(), line[5].strip(), line[6].strip(), ])
            else:
                writer.writerow(['', '', '', line[3].strip(), line[4].strip(), line[5].strip(), line[6].strip(), ])
            pre_name = line[0].strip()
            pre_product_id = line[1].strip()
            pre_date_order = line[2].strip()

    endTime=datetime.datetime.now()
    print("处理完成，耗时：%f" % (endTime-startTime).seconds)

def deal_purchase_repeat_data(filename, col=None):

    """deal repeat data"""
    startTime = datetime.datetime.now()
    print "开始处理..."
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        o = open('deal'+filename, 'wb')
        writer = csv.writer(o)
        pre_name = ''
        pre_product_id = ''
        pre_date_order = ''

        for line in reader:
            if not line[0]:
                continue
            if reader.line_num == 1:
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip(), line[3].strip(), line[4].strip(),
                                 line[5].strip(), line[6].strip(), line[7].strip(), line[8].strip(), line[9].strip(), ])
                continue
            if reader.line_num == 2:
                pre_name = line[0].strip()
                pre_product_id = line[1].strip()
                pre_date_order = line[2].strip()
                print pre_name, pre_product_id, pre_date_order
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip()+' 00:00:00', line[3].strip(), line[4].strip(),
                                 line[5].strip(), line[6].strip(),line[2],12, 'purchase.list0', ])
                continue
            if pre_name!=line[0].strip():
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip()+' 00:00:00', line[3].strip(), line[4].strip(),
                                 line[5].strip(), line[6].strip(),line[2],12, 'purchase.list0', ])
            else:
                writer.writerow(['', '', '', line[3].strip(), line[4].strip(),
                                    line[5].strip(), line[6].strip(),line[2]])

            pre_name = line[0].strip()
            pre_product_id = line[1].strip()
            pre_date_order = line[2].strip()

    endTime=datetime.datetime.now()
    print("处理完成，耗时：%f" % (endTime-startTime).seconds)


def deal_purchase_return_repeat_data(filename, col=None):

    """deal repeat data"""
    startTime = datetime.datetime.now()
    print "开始处理..."
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        o = open('deal'+filename, 'wb')
        writer = csv.writer(o)
        pre_name = ''
        pre_product_id = ''
        pre_date_order = ''

        for line in reader:
            if not line[0]:
                continue
            if reader.line_num == 1:
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip(), line[3].strip(), line[4].strip(),
                                 line[5].strip(), line[6].strip(), line[7].strip(), line[8].strip()])
                continue
            if reader.line_num == 2:
                pre_name = line[0].strip()
                pre_product_id = line[1].strip()
                pre_date_order = line[2].strip()
                print pre_name, pre_product_id, pre_date_order
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip()+' 00:00:00', line[3].strip(), line[4].strip(),
                                 line[5].strip(), 1, 9, 12])
                continue
            if pre_name!=line[0].strip():
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip()+' 00:00:00', line[3].strip(), line[4].strip(),
                                 line[5].strip(), 1, 9, 12 ])
            else:
                writer.writerow(['', '', '', line[3].strip(), line[4].strip(), line[5].strip(), 1, 9, 12])

            pre_name = line[0].strip()
            pre_product_id = line[1].strip()
            pre_date_order = line[2].strip()

    endTime=datetime.datetime.now()
    print("处理完成，耗时：%f" % (endTime-startTime).seconds)

def deal_sale_return_repeat_data(filename, col=None):

    """deal repeat data"""
    startTime = datetime.datetime.now()
    print "开始处理..."
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        o = open('deal'+filename, 'wb')
        writer = csv.writer(o)
        pre_name = ''
        pre_product_id = ''
        pre_date_order = ''

        for line in reader:
            if not line[0]:
                continue
            if reader.line_num == 1:
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip(), line[3].strip(), line[4].strip(),
                                 line[5].strip(), line[6].strip(), line[7].strip(), line[8].strip()])
                continue
            if reader.line_num == 2:
                pre_name = line[0].strip()
                pre_product_id = line[1].strip()
                pre_date_order = line[2].strip()
                print pre_name, pre_product_id, pre_date_order
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip()+' 00:00:00', line[3].strip(), line[4].strip(),
                                 line[5].strip(), 1, 12, 9])
                continue
            if pre_name!=line[0].strip():
                writer.writerow([line[0].strip(), line[1].strip(), line[2].strip()+' 00:00:00', line[3].strip(), line[4].strip(),
                                 line[5].strip(), 1, 12, 9 ])
            else:
                writer.writerow(['', '', '', line[3].strip(), line[4].strip(), line[5].strip(), 1, 12, 9])

            pre_name = line[0].strip()
            pre_product_id = line[1].strip()
            pre_date_order = line[2].strip()

    endTime=datetime.datetime.now()
    print("处理完成，耗时：%f" % (endTime-startTime).seconds)


def deal_partner_data(filename, col=None):

    """deal repeat data"""
    startTime = datetime.datetime.now()
    print "开始处理..."
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        o = open('deal'+filename, 'wb')
        writer = csv.writer(o)
        pre_name = ''

        for line in reader:
            if not line[0]:
                continue
            if reader.line_num == 1:
                continue
            partner = line[0].strip()
            no = partner.find('-')
            lbracket = partner.rfind('(')
            rbracket = partner.rfind(')')
            if int(no)>0:
                name = partner[:no].strip()
                ref = partner[lbracket+1:rbracket]
                #print ref,no
            else:
                name = partner
                ref = ''
            if reader.line_num == 2:
                pre_name = name
                writer.writerow([name, ref])
                continue
            if name == pre_name:
                continue
            else:
                #print name, pre_name, len(name), len(pre_name)
                pre_name = name
                writer.writerow([name, ref])


    endTime=datetime.datetime.now()
    print("处理完成，耗时：%f" % (endTime-startTime).seconds)

def deal_recipe_data(filename, col=None):

    """deal repeat data"""
    startTime = datetime.datetime.now()
    print "开始处理..."
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        o = open('deal'+filename, 'wb')
        writer = csv.writer(o)
        for line in reader:
            if reader.line_num == 1:
                writer.writerow(line)
                continue
            partner = line[0].strip()
            no = partner.find('-')
            if int(no)>0:
                name = partner[:no].strip()
            else:
                name = partner
            nline = line
            nline[0] = name
            writer.writerow(nline)
            continue

    endTime=datetime.datetime.now()
    print("处理完成，耗时：%f" % (endTime-startTime).seconds)

def deal_recipe_data_2(filename, col=None):

    """deal repeat data"""
    startTime = datetime.datetime.now()
    print "开始处理..."
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        o = open('deal'+filename, 'wb')
        writer = csv.writer(o)
        for line in reader:
            if reader.line_num == 1:
                writer.writerow([line[0].strip(), line[1].strip(), line[7].strip(), line[12].strip(), line[13].strip(),
                            line[14].strip(), line[15].strip(), line[16].strip(), line[17].strip()])
                continue
            partner = line[0].strip()
            no = partner.find('-')
            if int(no)>0:
                name = partner[:no].strip()
            else:
                name = partner
            note = ''
            for i in range(2, 11):
                note += line[i].strip()+ ','
            user = line[17].strip()
            print user,
            user = user.lower().capitalize()
            print user

            writer.writerow([name, line[1].strip(), note, line[12].strip(), line[13].strip(),
                            line[14].strip(), line[15].strip(), line[16].strip(), user])
            continue

    endTime=datetime.datetime.now()
    print("处理完成，耗时：%f" % (endTime-startTime).seconds)



#deal_sale_repeat_data('銷售資料-01.01-05.31.csv')
#deal_purchase_repeat_data('進貨明細-0101-0531(更新版).csv')
#deal_purchase_return_repeat_data('進貨退回-01.01-05.31.csv')
#deal_sale_return_repeat_data('銷貨退回-01.01-05.31.csv')
#deal_partner_data('purchasereturnpartner.csv')
#deal_recipe_data('客戶交易處方-01.01-05.31.csv')
deal_recipe_data_2('客戶交易處方-01.01-05.31.csv')

print "end scrip."
