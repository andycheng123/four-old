# -*- coding:utf-8 -*-
import sys
import xmlrpclib
import csv

def _check_args():
    if len(sys.argv) < 8:
        print 'wrong arg length, 6 expected but %d provided' % len(sys.argv)
        print 'execute format: python finish-order.py HOST-IP-ADDRESS PORT USERNAME PASSWORD DB-NAME FILE-NAME OrderType'
        print 'for example: python finish-order.py 0.0.0.0 8069 admin admin cu-four sale-names.csv [sale|purchase|sale_return|purchase_return]'
        return False
    else:
        return True

def main():
    if not _check_args():
        return
    HOST, PORT, user, pwd, db, csv_file, otype = sys.argv[1:8]

    root = 'http://%s:%d/xmlrpc/' % (HOST, int(PORT))
    uid = xmlrpclib.ServerProxy(root + 'common').login(db, user, pwd)
    print "Logged in as %s (uid: %d)" % (user, uid)
    sock = xmlrpclib.ServerProxy(root + 'object')
    reader = csv.reader(file(csv_file, 'rb'))
    reader.next()
    order_names = []
    for row in reader:
        if row[0]:
            order_names.append(row[0].strip())
    if otype == 'sale':
        sock.execute(db, uid, pwd, 'data.import', 'finish_sale', order_names)
        print "sale finish."
    if otype == 'purchase':
        sock.execute(db, uid, pwd, 'data.import', 'finish_purchase', order_names)
        print "purchase finish."
    ttype = ''
    if otype == 'sale_return':
        ttype == 'payment'
        sock.execute(db, uid, pwd, 'data.import', 'finish_return_order', order_names, ttype)
        print 'return order finish'
    if otype == 'purchase_return':
        ttype == 'receipt'
        sock.execute(db, uid, pwd, 'data.import', 'finish_return_order', order_names, ttype)
        print 'return order finish'

if __name__ == "__main__":
    main()
