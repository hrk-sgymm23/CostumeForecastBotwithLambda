import os
import random

import openai
import requests
from dotenv import load_dotenv

load_dotenv(verbose=True)
openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_weather_info():
    try:
        response_info = requests.get(os.environ.get("API_ENDPOINT")).json()
        return response_info
    except requests.RequestException as e:
        print("天気情報を取得できませんでした", e)

def parse_message(response_info):
    # 天気情報(文面)
    text = response_info["description"]["text"]

    #  降水確率、風向き、最高最低気温(三日分が配列で入っている)
    forecasts = response_info["forecasts"][0]
    # 空模様
    sky_appearance = forecasts["telop"]
    sky_appearance_detail = forecasts["detail"]["weather"]
    # 気温
    max_temp = forecasts["temperature"]["max"]["celsius"]
    min_temp = forecasts["temperature"]["min"]["celsius"]
    # 降水確率
    probability_rain_0to6 = forecasts["chanceOfRain"]["T00_06"]
    probability_rain_6to12 = forecasts["chanceOfRain"]["T06_12"]
    probability_rain_12to18 = forecasts["chanceOfRain"]["T12_18"]
    probability_rain_18to24 = forecasts["chanceOfRain"]["T18_24"]
    # f文字列を使って各値を埋め込み次の関数へ渡す
    weather_message = f"""
    ## 本日と明日の天気と気温の説明
    {text}

    ## 空模様
    {sky_appearance}
    ## 空模様の移り変わり
    {sky_appearance_detail}

    ## 最高気温
    {max_temp}
    ## 最低気温
    {min_temp}

    ## 0時から6時の降水確率
    {probability_rain_0to6}
    ## 6時から12時の降水確率
    {probability_rain_6to12}
    ## 12時から18時の降水確率
    {probability_rain_12to18}
    ## 18時から24時の降水確率
    {probability_rain_18to24}

    あなたは気象情報から適切な服装を導き出すプロの服装アドバイザーです。
    上記のテキスト群は本日の気象情報を説明するものになります。
    記載される記載情報の状況に適した服装を以下のフォーマットと注意事項に従って出力しなさい。

    <回答フォーマット例>
    🌤今日の衣装予報をお届け！
    今日は朝xx℃昼xx℃夜xx℃と「xxな日」です。
    服はxxやxx+xx/xx/xxが必要です。
    xxやxxでxx対策を！今日も素敵な1日をお過ごしください！

    <注意事項>
    - 140字以内で出力してください
    - 上着などといった抽象的なものではなくコートやダウンといった具体的ないるの名前をあげるようにしてください
    - 暑い場合はこまめな水分補給を！寒い場合は凍結に注意！など服装に関係ない場合も必要であれば入れてください
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

def choose_rails_article(recent_artilce: list[dict[str, str]]) -> list[dict[str, str]]:
    title_list = [article["title"] for article in recent_artilce]

    message = f"""
    RubyonRailsに関する記事を紹介するエキスパートです。
    以下は、RubyとRuby on railsに関する記事のタイトルリストです。
    エキスパートの観点から、活用方法や学び、tipsをシェアする記事を選定しなさい。
    選定基準と、記事リストは以下です。
    アウトプットは、テキストは一切不要で、記事タイトルのみ返してください。

    【選定基準】
    ・Rubyに関する記事またはRuby on railsに関する記事

    【記事リスト】
    {title_list}
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message},
        ],
    )
    rails_article_title = response["choices"][0]["message"]["content"]

    rails_article = [
        article for article in recent_artilce if article["title"] in rails_article_title
    ]

    return rails_article[0]


def summary_tweet(rails_article: list[dict[str, str]]) -> str:
    personality = f"""
    あなたはRubyとRuby on railsのプロです。
    次の記事タイトルに対して、プロの観点から、活用方法や学びをシェアします。
    
    回答フォーマットは以下です。
    タイトルのみが出力できれば良いです。
    説明文等は必要ありません。

    ※注意事項
    返答は140字以内で構成してください。
    繰り返します140字以内でお願いします!!!!!!   

    【回答フォーマット】
    🛑Ruby on Railsの記事を紹介🛑
    🗣「[記事のタイトル名]」

    https://zenn.dev/neet/articles/{rails_article["slug"]}
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": personality},
            {"role": "user", "content": rails_article["title"]},
        ],
    )
    return response["choices"][0]["message"]["content"]