# Author Tomo.K 2021/04/04
# This program is for AWS Lambda.
# Notify you of the chance to buy Amazon stock on SNS.
# The required requirement is to add the SNS ARN to the environment variable "SNS_ARN".
# Then add the following two layers to AWS.
# *** pandas_datareader ***
# ZIP "pandas_datareader" in the local environment and add it to the AWS layer.
# *** pandas ***
# arn:aws:lambda:ap-northeast-1:770693421928:layer:Klayers-python38-pandas:29

import boto3
import datetime
from pandas_datareader import data
import os

sns_arn = os.environ['SNS_ARN']

def get_stock(name, ref, day):
    rtn = 0
    try:
        df = data.DataReader(name, ref, day, day)
        rtn = df.iat[0, 3]
    except:
        rtn = 0
    return rtn

def get_stock_lastyear(name, ref, day):
    rtn = 0
    line = 0
    oldday = day + datetime.timedelta(days=-1)
    try:
        df = data.DataReader(name, ref, oldday, day)
        line = len(df) - 1
        rtn = df.iat[line, 3]
    except:
        rtn = 0
    return rtn

### MAIN ##############################################################
def lambda_handler(event, context):
    res = ''
    d_today = datetime.date.today()
    
    ### debug #####################################################
    #d_today = datetime.datetime.strptime('2020/03/12', '%Y/%m/%d')
    
    d_today = d_today + datetime.timedelta(hours=7) #ADD JAPAN TIME
    print (str(d_today))
    stock_today = get_stock('AMZN', 'yahoo', d_today)
    print (str(stock_today))
    
    if (stock_today == 0):
        res = 'stock_today non'
        return res
    
    d_lastyear = d_today + datetime.timedelta(days=-365)
    print (str(d_lastyear))
    stock_lastyear = get_stock_lastyear('AMZN', 'yahoo', d_lastyear)
    print (str(stock_lastyear))
    
    if (stock_lastyear == 0):
        res = 'stock_lastyear non'
        return res
    
    if (stock_today < stock_lastyear):
        print('buy now')
        sns = boto3.client('sns')
        subject = 'Amazon Stock Buy Now !!'
        message = subject + '\r\n' + \
                    str(d_today) + ': ' + str(stock_today) + '\r\n' + \
                    str(d_lastyear) + ': ' + str(stock_lastyear)
        response = sns.publish(
            TopicArn = sns_arn,
            Subject = subject,
            Message = message
        )
        res = message
        return res
    else:
        res = 'Not Buy'
        return res