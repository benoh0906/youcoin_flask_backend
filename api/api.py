import models
import urllib.request
import json

from flask import Blueprint, request, jsonify, g
from playhouse.shortcuts import model_to_dict

api=Blueprint('api','api',url_prefix="/api/v1")
key = ""

#rank Youcoin
@api.route('/main', methods = ["GET"])
def rank_youcoin():

    youcoins=[model_to_dict(youcoin) for youcoin in models.Youcoin.select().order_by(models.Youcoin.profit.desc()).limit(5)]

    return jsonify(data=youcoins, status={"code":200,"message":"success"})


#delete youcoin
@api.route('/delete/<id>', methods=["DELETE"])
def delete_youcoin(id):
    
    print('hit delete route')
    coin = model_to_dict(models.Youcoin.get(models.Youcoin.id==id))
    print(coin,"<-coin")
    coinUser=coin['user']['id']
    print(coinUser,'<-coinUser')
    coinProfit=coin['profit']
    user = model_to_dict(models.User.get(models.User.id==coinUser))

    profit = user["profit"]
    
    profitUpdate = models.User.update(profit=profit+coinProfit).where((models.User.id == coinUser))
    profitUpdate.execute()

    query = models.Youcoin.delete().where(models.Youcoin.id == id)
    query.execute()

    return jsonify(data='Success', status={"code":200, "message":"Success"})

#list youcoins
@api.route('/<id>', methods=["GET"])
def get_all_youcoins(id):
    # print(g.token,"<g token")
    try:
        youcoins=[model_to_dict(youcoin) for youcoin in models.Youcoin.select().where(models.Youcoin.user == int(id))]
        for data in youcoins:
            dataId=data['id']
            dataSN=data['startingNum']
            name=data["channelId"]
            data= urllib.request.urlopen("https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id="+name+"&key="+key).read()
            subs = json.loads(data)["items"][0]["statistics"]["subscriberCount"]
            
            query = models.Youcoin.update(currentNum=int(subs), profit=(int(subs)-dataSN)).where((models.Youcoin.user == int(id)) & (models.Youcoin.id==dataId))
            query.execute()

            # models.Stat.create(youcoin=dataId, currentSubs=subs)
            # stat=[model_to_dict(stat) for stat in models.Stat.select()]
            # print(len(stat),"<-num of stat")
        
        return jsonify(data=youcoins,status={"code":200,"message":"success"})

    except models.DoesNotExist:
        return jsonify(data={}, status={"code":401, "message":"There was an error getting the resource"})


#show youcoin
@api.route('/<id>',methods = ["GET"])
def show_youcoins():
    youcoin = models.Youcoin.get_by_id(id)
    return jsonify(data=model_to_dict(youcoin), status={"code":200,"message":"success"})

#create youcoin
@api.route('/', methods = ["POST"])
def create_youcoins():
    payload = request.get_json()
    
    user = models.User.get(models.User.id== payload['user'])
    
    url=payload["channelUrl"]
    
    for i in range(len(url)):
        if url[i:i+8]=="channel/":
            name=url[i+8:]

        elif url[i:i+5]=="user/":
            userFind=url[i+5:]
            subdata= urllib.request.urlopen("https://www.googleapis.com/youtube/v3/channels?part=statistics&forUsername="+userFind+"&key="+key).read()
            name=json.loads(subdata)["items"][0]["id"]
            print(name,"user name")
    
    data= urllib.request.urlopen("https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id="+name+"&key="+key).read()
    subs = json.loads(data)["items"][0]["statistics"]["subscriberCount"]
    title = json.loads(data)["items"][0]["snippet"]["title"]
    pic = json.loads(data)["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
    youcoin = models.Youcoin.create(
        user=user.id, 
        channelUrl=payload['channelUrl'],
        channelTitle= title,
        channelId = name,
        startingNum = int(subs),
        currentNum = int(subs),
        profit = 0,
        channelPic=pic
        )


    you_dict = model_to_dict(youcoin)

    return jsonify(data = you_dict, status={"code":281,"message":"Success"})
