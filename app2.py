#!/usr/bin/env python3

from flask import Flask, request, jsonify, url_for, send_from_directory, render_template, redirect
import plot_
from suds.client import Client


MMERCHANT_ID = '6a1d8dda-f647-11e9-bb51-000c295eb8fc'  # Required
ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'  # Required
amount = 1000  # Amount will be based on Toman  Required
description = u'توضیحات تراکنش تستی'  # Required
email = 'user@userurl.ir'  # Optional
mobile = '09123456789'  # Optional

app = Flask(__name__)

@app.route('/')
def render_static():
    return render_template('index.html')

@app.route("/bot/", methods=["POST"])
def plot():
    print(request.get_json())
    req = request.get_json()
    print(req)
    jpeg = plot_.generate_plot(req)
    home_url = request.url
    result = home_url + jpeg

    return jsonify(result)

@app.route("/bot/static/<path:path>")
def send_file(path):
    print(path)
    return send_from_directory("static", path)

@app.route('/payment-request/')
def send_request():
    amount = request.args.get('amount')
    description = request.args.get('description')
    client = Client(ZARINPAL_WEBSERVICE)
    result = client.service.PaymentRequest(MMERCHANT_ID,
                                           amount,
                                           description,
                                           mobile,
                                           email,
                                           str(url_for('verify', _external=True)))
    if result.Status == 100:
        print(result.Authority)
        return redirect('https://www.zarinpal.com/pg/StartPay/' + result.Authority)
    else:
        return 'Error'


@app.route('/verify/', methods=['GET', 'POST'])
def verify():
    client = Client(ZARINPAL_WEBSERVICE)
    print(request)
    if request.args.get('Status') == 'OK':
        result = client.service.PaymentVerification(MMERCHANT_ID,
                                                    request.args['Authority'],
                                                    amount)
        if result.Status == 100:
            return 'Transaction success. RefID: ' + str(result.RefID)
        elif result.Status == 101:
            return 'Transaction submitted : ' + str(result.Status)
        else:
            return 'Transaction failed. Status: ' + str(result.Status)
    else:
        result = client.service.PaymentVerification(MMERCHANT_ID,
                                                    request.args['Authority'],
                                                    amount)
        print(request.args['Authority'])
        return 'Transaction failed or canceled by user'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
