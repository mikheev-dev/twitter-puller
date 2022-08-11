from tweepy import Tweet, Response, Media
from typing import List, Dict


class TweetSerializer:
    @staticmethod
    def _prepare_media_keys_to_urls(media: List[Media]) -> Dict[str, str]:
        if not media:
            return {}
        media_keys_to_urls = {}
        for m in media:
            media_key = m.media_key
            if m.url:
                url = m.url
            elif m.preview_image_url:
                url = m.preview_image_url
            else:
                url = None
            if url:
                media_keys_to_urls.update({
                    media_key: url
                })
        return media_keys_to_urls

    @staticmethod
    def _extract_media_url_for_tweet(
            tweet: Tweet,
            media_keys_to_urls: Dict[str, str]
    ) -> List[str]:
        if not tweet.attachments:
            return []
        media_keys = tweet.attachments.get('media_keys')
        if not media_keys:
            return []
        tweet_media_urls = []
        for media_key in media_keys:
            media_url = media_keys_to_urls.get(media_key)
            if media_url:
                tweet_media_urls.append(media_url)
        return tweet_media_urls

    @staticmethod
    def serialize(response: Response, tags: List[str]) -> List[Dict]:
        if not response.data:
            return []
        media = response.includes.get('media')
        media_keys_to_urls = TweetSerializer._prepare_media_keys_to_urls(media=media)
        tweets = []
        for tweet in response.data:
            tweets.append(tweet.data)
            tweets[-1].update(
                {
                    'media_urls': TweetSerializer._extract_media_url_for_tweet(tweet, media_keys_to_urls),
                    'tags': tags,
                }
            )
        return tweets
