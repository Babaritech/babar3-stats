#!/usr/bin/env python

import config
import datetime
import flask
import json
import math
import operator
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.sql import *

from models import *

import sys
reload(sys)
sys.setdefaultencoding("latin-1")

def url(subpath):
    subpath = subpath[1:] if subpath[0]=='/' else subpath
    return '%s/%s' % (config.ROOT_DIR, subpath)


app = flask.Flask(
        __name__,
        static_folder = config.STATIC_FOLDER,
        static_url_path = url(config.STATIC_FOLDER)
        )

engine = sqlalchemy.create_engine(config._DBQUEUE, echo=False, isolation_level='READ_UNCOMMITTED', pool_recycle=60)
dbsession = sqlalchemy.orm.sessionmaker(bind=engine)()

@app.route(url('/'), methods=['GET'])
def index():

    return flask.render_template('index.html')


#################
#               #
#   CUSTOMERS   #
#               #
#################

@app.route(url('/customers'), methods=['GET'])
def customerstats():

    customers = dbsession.query(Customer).all()

    topdrinkers = dbsession.query(TotalPayment).order_by(TotalPayment.total.desc()).limit(20)

    return flask.render_template('customers.html', customers = customers, topdrinkers = topdrinkers)


@app.route(url('/customer/<int:id>'), methods=['GET'])
def statscustomer(id):

    PUR_HISTORY_LIMIT = 50
    PAY_HISTORY_LIMIT = 20

    # CUSTOMER
    customer = dbsession.query(Customer).filter_by(id=id).first()

    if customer is None:
        flask.abort(404)

    purchases = dbsession.query(Purchase).filter_by(customer_id=id).order_by(Purchase.timestamp.desc()).join(Product).all()
    payments = dbsession.query(Payment).filter_by(customer_id=id).order_by(Payment.timestamp.desc()).all()

    history = purchases[0:PUR_HISTORY_LIMIT]
    payhistory = payments[0:PAY_HISTORY_LIMIT]

    for elt in history:
        elt.quantity = 1 if elt.product.price==0 else int(math.ceil(elt.amount / elt.product.price))


    customer.balance = sum([e.amount for e in payments]) - sum([e.amount for e in purchases])
    customer.color = 'red' if (customer.balance + customer.status.overdraft)<0 else ''

    customer.alltime = sum([(e.amount) for e in payments])
    customer.last = '-' if len(purchases)==0 else purchases[0].timestamp

    customer.overdraft = "%.2f" % customer.status.overdraft

    if customer.status.overdraft>0:
        customer.overdraft = "-%s" % customer.overdraft


    # DRINKS
    drinks = {}
    for purchase in purchases:

        pid = purchase.product_id

        if pid not in drinks.keys():
            product = dbsession.query(Product).filter_by(id=pid).first()
            drinks[pid] = {'obj': product, 'count':0}

        if drinks[pid]['obj'].price==0:
            drinks[pid]['count'] += 1
        else:
            drinks[pid]['count'] += int(math.ceil(purchase.amount / drinks[pid]['obj'].price))

    ## http://stackoverflow.com/questions/613183/sort-a-python-dictionary-by-value
    countdict = {k:v['count'] for (k,v) in drinks.items()}
    scountdict = sorted(countdict.items(), key=operator.itemgetter(1), reverse=True)


    # RETURN
    return flask.render_template('customer.html', customer=customer, drinks=drinks, countdict=scountdict, history=history, payhistory=payhistory)


##############
#            #
#   DRINKS   #
#            #
##############

@app.route(url('/drinks'), methods=['GET'])
def drinksstats():

    drinks = dbsession.query(Product).all()
    ddrinks = {e.id:e for e in drinks}

    qtopdrinks = dbsession.query(TopProduct).order_by(TopProduct.amount.desc())
    qtopdrinks = {e.product_id:e for e in qtopdrinks}

    dtopdrinks = {}
    for k,v in qtopdrinks.items():
        if v.product.price==0:
            dtopdrinks[k] = v.count
        else:
            dtopdrinks[k] = int(math.ceil(v.amount / v.product.price))

    stopdrinks =  sorted(dtopdrinks.items(), key=operator.itemgetter(1), reverse=True)

    topdrinks = []
    for k,v in stopdrinks[:20]:
        topdrinks.append({'product':ddrinks[k], 'amount':v})

    return flask.render_template('drinks.html', drinks = drinks, topdrinks=topdrinks)


@app.route(url('/drink/<int:id>'), methods=['GET'])
def statsdrink(id):

    drink = dbsession.query(Product).filter_by(id=id).first()

    if drink is None:
        flask.abort(404)

    purchases = dbsession.query(Purchase).filter_by(product_id=drink.id).order_by(Purchase.timestamp.desc()).limit(20).all()
    cpurchases = dbsession.query(Purchase).filter_by(product_id=drink.id).all()

    customers = dbsession.query(Customer).all()
    customers = {e.id: e for e in customers}

    customerDrinks = {}

    for purchase in cpurchases:

        cid = purchase.customer.id
        if not cid in customerDrinks.keys():
            customerDrinks[cid] = 0

        if drink.price==0:
            customerDrinks[cid] += 1
        else:
            customerDrinks[cid] += int(math.ceil(purchase.amount / drink.price))

    scountdict = sorted(customerDrinks.items(), key=operator.itemgetter(1), reverse=True)
    topcustomers = []

    i=0
    TOP = 20
    for k,v in scountdict:
        topcustomers.append({'customer': customers[k], 'qty': v})
        i+=1
        if i>=TOP:
            break

    return flask.render_template('drink.html', drink=drink, purchases=purchases, topcustomers = topcustomers)


#####################
#                   #
#   MISCELLANEOUS   #
#                   #
#####################


@app.route(url('/misc/'), methods=['GET'])
def miscindex():

    return flask.render_template('miscindex.html')


@app.route(url('/misc/financial'), methods=['POST'])
def financialquery():

    ret = {}

    fmt = '%Y-%m-%d %H:%M:%S'
    dfrom = datetime.datetime.strptime(flask.request.form.get('dfrom'), fmt) - datetime.timedelta(hours=1)
    dto = datetime.datetime.strptime(flask.request.form.get('dto'), fmt) - datetime.timedelta(hours=1)

    payquery = dbsession.query(func.sum(Payment.amount).label('total_amount')).filter(Payment.timestamp >= dfrom).filter(Payment.timestamp <= dto).all()
    paytotal = 0 if payquery[0].total_amount is None else float(payquery[0].total_amount)

    purquery = dbsession.query(func.sum(Purchase.amount).label('total_amount')).filter(Purchase.timestamp >= dfrom).filter(Purchase.timestamp <= dto).all()
    purtotal = 0 if purquery[0].total_amount is None else float(purquery[0].total_amount)

    ret['payments'] = paytotal
    ret['purchases'] = purtotal

    return json.dumps(ret)



@app.teardown_request
def teardown_request(exception):
    if exception:
        dbsession.rollback()
        dbsession.close()
    dbsession.close()


def run_server():

    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        )


if __name__=='__main__':
    run_server()
