#モジュールのインストール################################################################################
from bs4 import BeautifulSoup
import datetime
from datetime import datetime as dt
import re
from dateutil import relativedelta
import pandas as pd
import requests


#前準備
cols=["タイトル","キャラ"]
df=pd.DataFrame(columns=cols)


#スクレイピング実装################################################################################
URL="https://imas-shinycolors.boom-app.wiki/entry/card-list" #シャニマスBoom-appさんのカード情報サイト
res=requests.get(URL)
soup=BeautifulSoup(res.content,"html.parser")

#テーブルごとにカード情報があるため、部分的に抽出する
tbody=soup.select("tbody")

#コミュのあるテーブルのみ取得する
comu_limit=6  #全8テーブル中、6テーブルがカード情報
countdf=0
for body in range(comu_limit):
  tr=tbody[body].select("tr")

  #trの数だけデータフレームに格納
  for i in range(len(tr)):
    card_list=[]
    text=tr[i].text

    #カード名、キャラ名の飾り文字をなくす処理
    splittext=text.split("【")[1]
    cardtitle=splittext.split("】")[0]
    card_name=splittext.split("】")[1]
    card_name=card_name.split("\n")[0]
    card_list.append(cardtitle)
    card_list.append(card_name)

    df.loc[countdf]=card_list
    countdf+=1


#データ補完作業################################################################################
#「アイドルロード」単体にコミュは存在しないので除外
df=df[df["タイトル"]!="アイドルロード"]

#カード名では取り出せない「WING」「ファン感謝祭」「GRAD」「Landing Point」「STEP」を人数分追加
unique_chara_arr=df["キャラ"].unique()

#タイトル文字を作成
WING_col="WING"
FUN_col="ファン感謝祭"
GRAD_col="GRAD"
LP_col="Landing Point"
STEP_col="STEP"
storytitle_list=[WING_col,FUN_col,GRAD_col,LP_col,STEP_col]

#シナリオごとのキャラストーリーを追加
for i in range(len(storytitle_list)):
  for j in range(len(unique_chara_arr)):
    story_insert_list=[]
    story_insert_list.append(storytitle_list[i])
    story_insert_list.append(unique_chara_arr[j])

    #最終行以降に追加でデータ挿入
    df.loc[countdf]=story_insert_list
    countdf+=1


#スプレッドシートに出力################################################################################
#モジュール読込、転記するスプレッドシートのアクセス認証
from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default

creds,_=default()
gc=gspread.authorize(creds)

Spr="シャニマスコミュ"
workbook=gc.open(Spr)                   #スプシ名の定義し、開く
worksheet=workbook.worksheet("シート2") #シート名の定義、開く

#転記範囲を指定し、出力
from gspread_dataframe import set_with_dataframe
set_with_dataframe(worksheet,df,row=1,col=1,include_index=False,resize=False) #resize：dataframeの形に合わせてスプレッドシートを操作する、index：index名をつけるか