import os

import tweepy
from dotenv import load_dotenv

import openai
import requests

load_dotenv(verbose=True)
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

def post_tweet(tweet: str) -> None:
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_KEY_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
    )

    client.create_tweet(text=tweet)


def lambda_handler():
    responce_info = get_weather_info()
    responce_temp_info = get_weather_temp_info()
    weather_info_message = parse_message(responce_info, responce_temp_info)
    recommend_costume_info = recommend_costume(weather_info_message)
    print(f"{recommend_costume_info=}")

    post_tweet(recommend_costume_info)

load_dotenv(verbose=True)
openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_weather_info():
    try:
        response_info = requests.get(os.environ.get("API_ENDPOINT")).json()
        return response_info
    except requests.RequestException as e:
        print("天気情報を取得できませんでした", e)

def get_weather_temp_info():
    try:
        response_temp_info = requests.get(os.environ.get("API_ENDPOINT2")).json()
        print(response_temp_info)
        return response_temp_info
    except requests.RequestException as e:
        print("気温情報を取得できませんでした", e)

def parse_message(response_info, response_temp_info):
    # 天気情報(文面)
    text = response_info["description"]["text"]

    #  降水確率、風向き、最高最低気温(三日分が配列で入っている)
    forecasts = response_info["forecasts"][0]
    # 空模様
    sky_appearance = forecasts["telop"]
    sky_appearance_detail = forecasts["detail"]["weather"]
    # 降水確率
    probability_rain_0to6 = forecasts["chanceOfRain"]["T00_06"]
    probability_rain_6to12 = forecasts["chanceOfRain"]["T06_12"]
    probability_rain_12to18 = forecasts["chanceOfRain"]["T12_18"]
    probability_rain_18to24 = forecasts["chanceOfRain"]["T18_24"]

    # 気温
    # max_temp = forecasts["temperature"]["max"]["celsius"]
    # max_temp = forecasts["temperature"]["max"]["celsius"]
    # min_temp = forecasts["temperature"]["min"]["celsius"]

    temps = []
    for entry in response_temp_info:
        for series in entry["timeSeries"]:
            for area_data in series["areas"]:
                if "temps" in area_data:
                    temps.extend(area_data["temps"])
    max_temp = temps[0]
    min_temp = temps[1]

    # f文字列を使って各値を埋め込み次の関数へ渡す
    weather_message = f"""
    ```
    ## 本日と明日の天気と気温の説明
    {text}

    ## 空模様
    {sky_appearance}
    ## 空模様の移り変わり
    {sky_appearance_detail}

    # 以下観測地点 東京の情報
    ## 最高気温
    {max_temp}
    ## 最低気温
    {min_temp}
    (※気温情報がNone)と表示される場合,気温に関する情報の文は出力しないでください

    ## 0時から6時の降水確率
    {probability_rain_0to6}
    ## 6時から12時の降水確率
    {probability_rain_6to12}
    ## 12時から18時の降水確率
    {probability_rain_12to18}
    ## 18時から24時の降水確率
    {probability_rain_18to24}
    ```
    
    あなたは気象情報から適切な服装を導き出すプロの服装アドバイザーです。
    上記のテキスト群は本日の気象情報を説明するものになります。
    記載される記載情報の状況に適した服装を以下のフォーマットと注意事項に従って出力しなさい。

    <回答フォーマット例>
    🌤今日の都内の衣装予報をお届け！
    今日は朝xx℃昼xx℃夜xx℃と「xxな日」です。
    服はxxやxx+xx/xx/xxが必要です。
    xxやxxでxx対策を！今日も素敵な1日をお過ごしください！

    <注意事項>
    - <重要事項！！>140字以内で出力してください
    - 「🌤今日の都内の衣装予報をお届け！」を必ず先頭文としてください(関東甲信越ではなく都内と言い切ってください)
    - 「本日は最高気温xx℃最低温はxx℃」と「xxな日」です。」の一文は必ず入れてください
    - 適切な服装の提案はより詳細に
        - 各時間帯の服装を提案を必ず入れてください
        - 上着やインナーなどといった抽象的なものではなくコートやダウンといった具体的な衣類の名前をあげるようにしてください      
        - 服装の組み合わせも明確にしてください
            - インナーはスェットかセーターなのかそれともシャツでいいのか
            - アウターはコートやダウンがいいのかそれともライトなジャケットがいいのか
    - 「今日も素敵な1日をお過ごしください！」を最後の一文に必ず入れてください
    - <重要事項！！>140字以内で出力してください
    """
    

    print(weather_message)

    return weather_message


def recommend_costume(weather_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": weather_message},
        ],
    )
    recommend_costume_message = response["choices"][0]["message"]["content"]

    return recommend_costume_message

lambda_handler()