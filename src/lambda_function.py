import os

import tweepy
from dotenv import load_dotenv

from module import recommend_costume, get_weather_info

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
    weather_info_message = get_weather_info()
    # recommend_costume_info = recommend_costume(weather_info_message)
    # print(f"{recommend_costume_info=}")

    # post_tweet(recommend_costume_info)


lambda_handler()