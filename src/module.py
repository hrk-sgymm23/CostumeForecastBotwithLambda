import os
import random

import openai
import requests
from dotenv import load_dotenv

load_dotenv(verbose=True)
openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_weather_info():
    response_info = requests.get(os.environ.get("API_ENDPOINT")).json()
    # 天気情報(文面)
    # 関東甲信地方は高気圧に覆われていますが、気圧の谷や寒気の影響を受けています。東京地方は、曇りで雨の降っている所があります。
    # １１日は、気圧の谷や寒気の影響を受けるため、曇りで、雷を伴って雨や雪の降る所があるでしょう。伊豆諸島では、雨や雷雨となる所がある見込みです。
    # １２日は、はじめ気圧の谷や寒気の影響を受けますが、次第に高気圧に覆われるでしょう。このため、曇りで朝まで雷を伴って雪や雨の降る所がありますが、昼前からは晴れるでしょう。伊豆諸島では、雨や雷雨となる所がある見込みです。
    # 【関東甲信地方】
    # 関東甲信地方は、晴れや曇りで、雨や雪の降っている所があります。
    # １１日は、高気圧に覆われますが、気圧の谷や寒気の影響を受ける見込みです。このため、曇りや晴れで、雷を伴って雨や雪の降る所があるでしょう。
    # １２日は、はじめ気圧の谷や寒気の影響を受けますが、次第に高気圧に覆われるでしょう。このため、曇りのち晴れで、午前中は雷を伴って雪や雨の降る所がある見込みです。
    # 関東地方と伊豆諸島の海上では、１１日はうねりを伴い波が高く、１２日はしけるでしょう。船舶は高波に注意してください。
    text = response_info["description"]["text"]

    #  降水確率、風向き、最高最低気温(三日分が配列で入っている)
    # {'date': '2024-02-11', 'dateLabel': '今日', 'telop': '曇り', 'detail': {'weather': 'くもり\u3000所により\u3000雨か雪\u3000で\u3000雷を伴う', 'wind': '北の風', 'wave': '０．５メートル'}, 'temperature': {'min': {'celsius': None, 'fahrenheit': None}, 'max': {'celsius': None, 'fahrenheit': None}}, 'chanceOfRain': {'T00_06': '--%', 'T06_12': '--%', 'T12_18': '--%', 'T18_24': '30%'}, 'image': {'title': '曇り', 'url': 'https://www.jma.go.jp/bosai/forecast/img/200.svg', 'width': 80, 'height': 60}}
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
    """
    
    print(weather_message)

    return weather_message


def recommend_costume():
    return

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