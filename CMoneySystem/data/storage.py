"""数据存储模块"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from main import db
from models.stock_analysis import StockAnalysis, NewsData, FinancialReport, MacroEconomicData
from models.prediction import PredictionResult, StockPriceHistory, AnalysisTask


class DataStorage:
    """数据存储类"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def save_analysis_result(self, analysis_data: Dict[str, Any]) -> Optional[int]:
        """
        保存分析结果

        Args:
            analysis_data: 分析结果数据

        Returns:
            记录ID，失败返回None
        """
        try:
            analysis_results = analysis_data.get('analysis_results', {})

            stock_analysis = StockAnalysis(
                stock_code=analysis_data['stock_code'],
                analysis_type=analysis_data['analysis_type'],
                time_horizon=analysis_data['time_horizon'],
                comprehensive_score=analysis_data.get('comprehensive_score'),
                fundamental_score=analysis_results.get('fundamental', {}).get('score'),
                macro_economic_score=analysis_results.get('macro_economic', {}).get('score'),
                industry_score=analysis_results.get('industry', {}).get('score'),
                policy_score=analysis_results.get('policy', {}).get('score'),
                international_score=analysis_results.get('international', {}).get('score'),
                funding_score=analysis_results.get('funding', {}).get('score'),
                market_structure_score=analysis_results.get('market_structure', {}).get('score'),
                technical_score=analysis_results.get('technical', {}).get('score'),
                sentiment_score=analysis_results.get('sentiment', {}).get('score'),
                analysis_details=analysis_results,
                recommendation=analysis_data.get('recommendation')
            )

            db.session.add(stock_analysis)
            db.session.commit()

            self.logger.info(f"Saved analysis result for {analysis_data['stock_code']}, ID: {stock_analysis.id}")
            return stock_analysis.id

        except Exception as e:
            self.logger.error(f"Error saving analysis result: {e}")
            db.session.rollback()
            return None

    def save_prediction_result(self, prediction_data: Dict[str, Any]) -> Optional[int]:
        """
        保存预测结果

        Args:
            prediction_data: 预测结果数据

        Returns:
            记录ID，失败返回None
        """
        try:
            prediction = PredictionResult(
                stock_code=prediction_data['stock_code'],
                time_horizon=prediction_data['time_horizon'],
                horizon_name=prediction_data['horizon_name'],
                horizon_days=prediction_data['horizon_days'],
                trend=prediction_data['trend'],
                trend_name=prediction_data['trend_name'],
                confidence=prediction_data['confidence'],
                price_change_pct=prediction_data.get('price_change_pct'),
                risk_level=prediction_data.get('risk_level'),
                key_factors=prediction_data.get('key_factors'),
                summary=prediction_data.get('summary'),
                prediction_details=prediction_data
            )

            db.session.add(prediction)
            db.session.commit()

            self.logger.info(f"Saved prediction result for {prediction_data['stock_code']}, ID: {prediction.id}")
            return prediction.id

        except Exception as e:
            self.logger.error(f"Error saving prediction result: {e}")
            db.session.rollback()
            return None

    def save_news_data(self, news_item: Dict[str, Any]) -> Optional[int]:
        """
        保存新闻数据

        Args:
            news_item: 新闻数据

        Returns:
            记录ID，失败返回None
        """
        try:
            news = NewsData(
                stock_code=news_item['stock_code'],
                title=news_item['title'],
                content=news_item.get('content'),
                source=news_item.get('source'),
                url=news_item.get('url'),
                sentiment_score=news_item.get('sentiment_score'),
                sentiment_label=news_item.get('sentiment'),
                keywords=news_item.get('keywords'),
                publish_time=datetime.fromisoformat(news_item['publish_time']) if news_item.get('publish_time') else None
            )

            db.session.add(news)
            db.session.commit()

            self.logger.info(f"Saved news data, ID: {news.id}")
            return news.id

        except Exception as e:
            self.logger.error(f"Error saving news data: {e}")
            db.session.rollback()
            return None

    def save_price_history(self, price_data: Dict[str, Any]) -> Optional[int]:
        """
        保存股价历史数据

        Args:
            price_data: 价格数据

        Returns:
            记录ID，失败返回None
        """
        try:
            # 检查是否已存在
            existing = StockPriceHistory.query.filter_by(
                stock_code=price_data['stock_code'],
                trade_date=price_data['trade_date']
            ).first()

            if existing:
                self.logger.info(f"Price data already exists for {price_data['stock_code']} on {price_data['trade_date']}")
                return existing.id

            price_history = StockPriceHistory(
                stock_code=price_data['stock_code'],
                trade_date=price_data['trade_date'],
                open_price=price_data.get('open'),
                high_price=price_data.get('high'),
                low_price=price_data.get('low'),
                close_price=price_data.get('close'),
                volume=price_data.get('volume'),
                turnover=price_data.get('turnover'),
                change_pct=price_data.get('change_pct'),
                change_amount=price_data.get('change_amount')
            )

            db.session.add(price_history)
            db.session.commit()

            self.logger.info(f"Saved price history for {price_data['stock_code']}, ID: {price_history.id}")
            return price_history.id

        except Exception as e:
            self.logger.error(f"Error saving price history: {e}")
            db.session.rollback()
            return None

    def get_latest_analysis(self, stock_code: str, limit: int = 10) -> List[Dict]:
        """
        获取最新的分析结果

        Args:
            stock_code: 股票代码
            limit: 返回数量

        Returns:
            分析结果列表
        """
        try:
            results = StockAnalysis.query.filter_by(
                stock_code=stock_code
            ).order_by(
                StockAnalysis.created_at.desc()
            ).limit(limit).all()

            return [result.to_dict() for result in results]

        except Exception as e:
            self.logger.error(f"Error getting latest analysis: {e}")
            return []

    def get_latest_prediction(self, stock_code: str, time_horizon: str = None) -> Optional[Dict]:
        """
        获取最新的预测结果

        Args:
            stock_code: 股票代码
            time_horizon: 时间范围

        Returns:
            预测结果字典
        """
        try:
            query = PredictionResult.query.filter_by(stock_code=stock_code)

            if time_horizon:
                query = query.filter_by(time_horizon=time_horizon)

            result = query.order_by(
                PredictionResult.prediction_date.desc()
            ).first()

            return result.to_dict() if result else None

        except Exception as e:
            self.logger.error(f"Error getting latest prediction: {e}")
            return None

    def get_price_history(self, stock_code: str, days: int = 30) -> List[Dict]:
        """
        获取股价历史数据

        Args:
            stock_code: 股票代码
            days: 天数

        Returns:
            价格数据列表
        """
        try:
            results = StockPriceHistory.query.filter_by(
                stock_code=stock_code
            ).order_by(
                StockPriceHistory.trade_date.desc()
            ).limit(days).all()

            return [result.to_dict() for result in reversed(results)]

        except Exception as e:
            self.logger.error(f"Error getting price history: {e}")
            return []

    def save_task(self, task_data: Dict[str, Any]) -> Optional[str]:
        """
        保存分析任务

        Args:
            task_data: 任务数据

        Returns:
            任务ID，失败返回None
        """
        try:
            task = AnalysisTask(
                task_id=task_data['task_id'],
                stock_code=task_data['stock_code'],
                analysis_type=task_data['analysis_type'],
                time_horizon=task_data.get('time_horizon'),
                status=task_data.get('status', 'pending'),
                progress=task_data.get('progress', 0),
                parameters=task_data.get('parameters')
            )

            db.session.add(task)
            db.session.commit()

            self.logger.info(f"Saved task {task.task_id}")
            return task.task_id

        except Exception as e:
            self.logger.error(f"Error saving task: {e}")
            db.session.rollback()
            return None

    def update_task_status(self, task_id: str, status: str, progress: int = None,
                          result: Dict = None, error_message: str = None) -> bool:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 状态
            progress: 进度
            result: 结果
            error_message: 错误消息

        Returns:
            是否成功
        """
        try:
            task = AnalysisTask.query.filter_by(task_id=task_id).first()

            if not task:
                self.logger.error(f"Task {task_id} not found")
                return False

            task.status = status
            if progress is not None:
                task.progress = progress
            if result is not None:
                task.result = result
            if error_message is not None:
                task.error_message = error_message

            if status == 'running' and not task.started_at:
                task.started_at = datetime.utcnow()
            elif status in ['completed', 'failed']:
                task.completed_at = datetime.utcnow()

            db.session.commit()

            self.logger.info(f"Updated task {task_id} status to {status}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating task status: {e}")
            db.session.rollback()
            return False

    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        获取任务信息

        Args:
            task_id: 任务ID

        Returns:
            任务信息字典
        """
        try:
            task = AnalysisTask.query.filter_by(task_id=task_id).first()
            return task.to_dict() if task else None

        except Exception as e:
            self.logger.error(f"Error getting task: {e}")
            return None

    def delete_old_data(self, days: int = 90) -> int:
        """
        删除过期数据

        Args:
            days: 保留天数

        Returns:
            删除记录数
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            count = 0

            # 删除旧的分析结果
            old_analyses = StockAnalysis.query.filter(
                StockAnalysis.created_at < cutoff_date
            ).all()
            count += len(old_analyses)
            for analysis in old_analyses:
                db.session.delete(analysis)

            # 删除旧的预测结果
            old_predictions = PredictionResult.query.filter(
                PredictionResult.created_at < cutoff_date
            ).all()
            count += len(old_predictions)
            for prediction in old_predictions:
                db.session.delete(prediction)

            db.session.commit()

            self.logger.info(f"Deleted {count} old records")
            return count

        except Exception as e:
            self.logger.error(f"Error deleting old data: {e}")
            db.session.rollback()
            return 0
