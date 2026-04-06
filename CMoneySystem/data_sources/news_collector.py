"""新闻数据采集模块

支持多种新闻源：
- 财经网站 RSS 订阅
- 官方媒体和地方媒体报道
- 社交媒体情感分析
- 交易所公告
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import re

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    logging.warning("feedparser not installed. Install with: pip install feedparser")


class NewsDataSource:
    """新闻数据源"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.name = "NewsCollector"

        # 主要新闻 RSS 源
        self.rss_sources = {
            'sina_finance': 'http://finance.sina.com.cn/roll/index.d.html',  # 新浪财经
            'eastmoney': 'http://finance.eastmoney.com/a/cjkj.html',  # 东方财富
            'wallstreetcn': 'https://wallstreetcn.com/rss',  # 华尔街见闻
            'jrj': 'http://finance.jrj.com.cn/',  # 金融界
        }

        # 官方媒体和地方媒体
        self.official_media = {
            'xinhua': 'http://www.xinhuanet.com/finance/news_fortune.xml',  # 新华网财经
            'people': 'http://finance.people.com.cn/GB/392159/index.html',  # 人民网财经
            'cctv': 'http://finance.cctv.com/',  # 央视财经
            'chinanews': 'http://www.chinanews.com/finance.shtml',  # 中国新闻网财经
        }

        # 地方媒体（各省市官方媒体）
        self.local_media = {
            'beijing': 'http://www.beijing.gov.cn/zwgk/',  # 首都之窗
            'shanghai': 'http://www.shanghai.gov.cn/',  # 上海市政府
            'guangdong': 'http://www.gd.gov.cn/',  # 广东省政府
            'shenzhen': 'http://www.sz.gov.cn/',  # 深圳市政府
            'zhejiang': 'http://www.zj.gov.cn/',  # 浙江省政府
            'jiangsu': 'http://www.jiangsu.gov.cn/',  # 江苏省政府
            'sichuan': 'http://www.sc.gov.cn/',  # 四川省政府
            'shandong': 'http://www.shandong.gov.cn/',  # 山东省政府
            'hubei': 'http://www.hubei.gov.cn/',  # 湖北省政府
            'henan': 'http://www.henan.gov.cn/',  # 河南省政府
        }

        # 交易所公告源
        self.exchange_sources = {
            'sse': 'http://www.sse.com.cn/disclosure/listedinfo/announcement/',  # 上交所
            'szse': 'http://www.szse.cn/disclosure/list/',  # 深交所
            'csrc': 'http://www.csrc.gov.cn/',  # 证监会
        }

    def fetch_rss_news(self, source_url: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        从 RSS 源获取新闻

        Args:
            source_url: RSS 源地址
            limit: 最多获取的新闻数量

        Returns:
            新闻列表
        """
        if not FEEDPARSER_AVAILABLE:
            self.logger.error("feedparser not installed")
            return []

        try:
            feed = feedparser.parse(source_url)

            news_list = []
            for entry in feed.entries[:limit]:
                news_item = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'author': entry.get('author', ''),
                    'tags': [tag.term for tag in entry.get('tags', [])],
                    'timestamp': datetime.now().isoformat(),
                    'source': source_url
                }
                news_list.append(news_item)

            self.logger.info(f"Fetched {len(news_list)} news from {source_url}")
            return news_list

        except Exception as e:
            self.logger.error(f"Error fetching RSS from {source_url}: {e}")
            return []

    def fetch_http_news(self, url: str, headers: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        从 HTTP 网页获取新闻（简化版，实际应用需要更复杂的解析）

        Args:
            url: 网页 URL
            headers: 请求头

        Returns:
            新闻列表
        """
        if not REQUESTS_AVAILABLE:
            return []

        try:
            if headers is None:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # 简化实现：实际应用需要使用 BeautifulSoup 等工具解析
            # 这里返回空列表，表示需要进一步实现
            self.logger.warning(f"HTTP news parsing not fully implemented for {url}")
            return []

        except Exception as e:
            self.logger.error(f"Error fetching HTTP news from {url}: {e}")
            return []

    def get_financial_news(self, stock_code: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取财经新闻

        Args:
            stock_code: 股票代码（可选，用于筛选相关新闻）
            limit: 新闻数量限制

        Returns:
            新闻列表
        """
        all_news = []

        # 从各个 RSS 源获取新闻
        for source_name, url in self.rss_sources.items():
            if url.endswith('.xml') or url.endswith('.rss'):
                news_list = self.fetch_rss_news(url, limit=limit // len(self.rss_sources))
            else:
                news_list = self.fetch_http_news(url)

            # 筛选相关新闻
            if stock_code:
                news_list = self._filter_relevant_news(news_list, stock_code)

            all_news.extend(news_list)

        # 按时间排序
        all_news.sort(key=lambda x: x.get('published', ''), reverse=True)

        self.logger.info(f"Collected {len(all_news)} financial news")
        return all_news[:limit]

    def get_official_media_news(self, limit: int = 30) -> List[Dict[str, Any]]:
        """
        获取官方媒体报道

        Args:
            limit: 新闻数量限制

        Returns:
            新闻列表
        """
        all_news = []

        for media_name, url in self.official_media.items():
            if url.endswith('.xml') or url.endswith('.rss'):
                news_list = self.fetch_rss_news(url, limit=limit // len(self.official_media))
            else:
                news_list = self.fetch_http_news(url)

            all_news.extend(news_list)

        self.logger.info(f"Collected {len(all_news)} official media news")
        return all_news[:limit]

    def get_local_media_news(self, regions: List[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取地方媒体报道

        Args:
            regions: 地区列表（如 ['beijing', 'shanghai']），None 表示全部
            limit: 新闻数量限制

        Returns:
            新闻列表
        """
        if regions is None:
            regions = list(self.local_media.keys())

        all_news = []

        for region in regions:
            if region not in self.local_media:
                continue

            url = self.local_media[region]
            if url.endswith('.xml') or url.endswith('.rss'):
                news_list = self.fetch_rss_news(url, limit=10)
            else:
                news_list = self.fetch_http_news(url)

            # 标记地区
            for news_item in news_list:
                news_item['region'] = region

            all_news.extend(news_list)

        self.logger.info(f"Collected {len(all_news)} local media news")
        return all_news[:limit]

    def get_exchange_announcements(self, exchange: str = 'sse', stock_code: str = None,
                                   limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取交易所公告

        Args:
            exchange: 交易所代码 (sse=上交所, szse=深交所, csrc=证监会)
            stock_code: 股票代码（可选）
            limit: 公告数量限制

        Returns:
            公告列表
        """
        if exchange not in self.exchange_sources:
            self.logger.error(f"Unknown exchange: {exchange}")
            return []

        url = self.exchange_sources[exchange]

        # 简化实现
        # 实际应用需要根据交易所的 API 或网页结构进行解析
        self.logger.warning(f"Exchange announcement parsing not fully implemented for {exchange}")

        # 模拟返回
        return []

    def _filter_relevant_news(self, news_list: List[Dict[str, Any]], stock_code: str) -> List[Dict[str, Any]]:
        """
        筛选与特定股票相关的新闻

        Args:
            news_list: 新闻列表
            stock_code: 股票代码

        Returns:
            筛选后的新闻列表
        """
        relevant_news = []

        # 简单的关键词匹配
        keywords = [stock_code]

        # 可以扩展为搜索股票名称
        # keywords.append(stock_name)

        for news in news_list:
            title = news.get('title', '').lower()
            summary = news.get('summary', '').lower()

            for keyword in keywords:
                if keyword.lower() in title or keyword.lower() in summary:
                    relevant_news.append(news)
                    break

        return relevant_news

    def collect_all_news(self, stock_code: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        收集所有类型的新闻

        Args:
            stock_code: 股票代码（可选）

        Returns:
            分类新闻字典
        """
        result = {
            'financial_news': self.get_financial_news(stock_code),
            'official_media': self.get_official_media_news(),
            'local_media': self.get_local_media_news(),
            'exchange_announcements': []
        }

        if stock_code:
            # 获取该股票的交易所公告
            exchange = 'sse' if stock_code.startswith('6') else 'szse'
            result['exchange_announcements'] = self.get_exchange_announcements(
                exchange=exchange,
                stock_code=stock_code
            )

        total_news = sum(len(news) for news in result.values())
        self.logger.info(f"Collected total {total_news} news items")

        return result

    def save_news_to_file(self, news_data: Dict[str, Any], filename: str):
        """
        将新闻数据保存到文件

        Args:
            news_data: 新闻数据
            filename: 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Saved news data to {filename}")

        except Exception as e:
            self.logger.error(f"Error saving news data: {e}")


class SentimentAnalyzer:
    """情感分析器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 简化的情感词典
        self.positive_words = [
            '上涨', '大涨', '增长', '盈利', '利好', '突破', '创新高',
            '强势', '牛市', '繁荣', '增长', '提升', '改善', '优异',
            '成功', '扩张', '收益', '利润', '积极', '看好', '推荐',
            '买入', '增持', '超预期', '优异', '领先', '优势'
        ]

        self.negative_words = [
            '下跌', '大跌', '暴跌', '亏损', '利空', '跌破', '创新低',
            '弱势', '熊市', '衰退', '下降', '下滑', '恶化', '疲软',
            '失败', '收缩', '损失', '负债', '消极', '看空', '推荐卖出',
            '减持', '低于预期', '风险', '危机', '问题', '下滑'
        ]

        try:
            # 尝试使用更高级的情感分析库
            import snownlp
            self.snownlp_available = True
        except ImportError:
            self.snownlp_available = False
            self.logger.warning("snownlp not installed. Install with: pip install snownlp")

    def analyze_sentiment_simple(self, text: str) -> Dict[str, Any]:
        """
        简单的情感分析（基于关键词）

        Args:
            text: 待分析文本

        Returns:
            情感分析结果
        """
        positive_count = 0
        negative_count = 0

        for word in self.positive_words:
            if word in text:
                positive_count += text.count(word)

        for word in self.negative_words:
            if word in text:
                negative_count += text.count(word)

        total = positive_count + negative_count

        if total == 0:
            sentiment = 'neutral'
            score = 0.0
        else:
            score = (positive_count - negative_count) / total
            if score > 0.2:
                sentiment = 'positive'
            elif score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

        return {
            'sentiment': sentiment,  # positive/negative/neutral
            'score': score,  # -1 to 1
            'positive_count': positive_count,
            'negative_count': negative_count,
            'confidence': min(total / 10, 1.0)  # 简单的置信度估算
        }

    def analyze_sentiment_advanced(self, text: str) -> Dict[str, Any]:
        """
        高级情感分析（使用 SnowNLP）

        Args:
            text: 待分析文本

        Returns:
            情感分析结果
        """
        if not self.snownlp_available:
            return self.analyze_sentiment_simple(text)

        try:
            from snownlp import SnowNLP

            s = SnowNLP(text)
            score = s.sentiments  # 0 to 1, 1 is positive

            # 转换为 -1 to 1
            adjusted_score = (score - 0.5) * 2

            if adjusted_score > 0.2:
                sentiment = 'positive'
            elif adjusted_score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            return {
                'sentiment': sentiment,
                'score': adjusted_score,
                'raw_score': score,
                'method': 'snownlp'
            }

        except Exception as e:
            self.logger.error(f"Error in advanced sentiment analysis: {e}")
            return self.analyze_sentiment_simple(text)

    def analyze_news_sentiment(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析新闻列表的整体情感

        Args:
            news_list: 新闻列表

        Returns:
            整体情感分析结果
        """
        if not news_list:
            return {
                'overall_sentiment': 'neutral',
                'average_score': 0.0,
                'news_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }

        total_score = 0.0
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for news in news_list:
            # 合并标题和摘要进行分析
            text = news.get('title', '') + ' ' + news.get('summary', '')

            result = self.analyze_sentiment_advanced(text)

            total_score += result.get('score', 0)

            if result['sentiment'] == 'positive':
                positive_count += 1
            elif result['sentiment'] == 'negative':
                negative_count += 1
            else:
                neutral_count += 1

        average_score = total_score / len(news_list) if news_list else 0

        # 判断整体情感
        if average_score > 0.1:
            overall_sentiment = 'positive'
        elif average_score < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        return {
            'overall_sentiment': overall_sentiment,
            'average_score': average_score,
            'news_count': len(news_list),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_ratio': positive_count / len(news_list) if news_list else 0,
            'negative_ratio': negative_count / len(news_list) if news_list else 0
        }

    def analyze_market_sentiment(self, stock_code: str = None) -> Dict[str, Any]:
        """
        分析市场情绪

        Args:
            stock_code: 股票代码（可选）

        Returns:
            市场情绪分析结果
        """
        collector = NewsDataSource()

        # 收集新闻
        all_news = collector.collect_all_news(stock_code)

        # 分析各类新闻的情感
        sentiment_results = {}

        for news_type, news_list in all_news.items():
            if news_list:
                sentiment_results[news_type] = self.analyze_news_sentiment(news_list)

        # 计算整体市场情绪
        all_news_list = []
        for news_list in all_news.values():
            all_news_list.extend(news_list)

        overall_sentiment = self.analyze_news_sentiment(all_news_list)

        return {
            'overall': overall_sentiment,
            'by_type': sentiment_results,
            'timestamp': datetime.now().isoformat()
        }
