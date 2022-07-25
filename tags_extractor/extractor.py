from typing import List, Dict

from lib.event import Event, FullParsedTweetBody
from lib.service.service import PipelineService


class TagsExtractorService(PipelineService):
    @staticmethod
    def _extract_hashtags(tweet: Dict) -> List[str]:
        if not tweet.get('entities'):
            return []
        entities_hashtags = tweet['entities'].get('hashtags')
        if not entities_hashtags:
            return []
        hashtags = []
        for hashtag in entities_hashtags:
            if not hashtag:
                continue
            tag = hashtag.get('tag')
            if not tag:
                continue
            hashtags.append(tag)
        return hashtags

    @staticmethod
    def _extract_media_urls(tweet: Dict) -> List[str]:
        media_urls = tweet.get('media_urls')
        if not media_urls:
            return []
        return media_urls

    @staticmethod
    def _check_is_retweet(tweet: Dict) -> bool:
        referenced_tweets = tweet.get('referenced_tweets')
        if not referenced_tweets:
            return False
        type = referenced_tweets[0].get('type')
        if not type:
            return False
        return type == 'retweeted'

    def handle_event(self, event: Event) -> Event:
        tweet: Dict = event.body
        hashtags = self._extract_hashtags(tweet=tweet)
        media_urls = self._extract_media_urls(tweet=tweet)
        is_retweet = self._check_is_retweet(tweet)
        return Event(
            type='parsed',
            body=FullParsedTweetBody(
                tweet_id=tweet['id'],
                user_id=tweet['author_id'],
                tags=hashtags,
                txt=tweet['text'],
                is_retweet=is_retweet,
                media=media_urls,
                created_at=tweet['created_at'],
            )
        )
