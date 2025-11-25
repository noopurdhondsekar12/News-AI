from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from ..app.core.database import db_service
from ..app.services.uniguru import uniguru_service
from ..agents.agent_registry import agent_registry

class RLFeedbackService:
    def __init__(self):
        self.reward_threshold = 0.6  # Minimum acceptable reward score
        self.max_correction_attempts = 3

    async def calculate_reward(self, news_item: Dict[str, Any], script_output: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive reward score for news processing output"""
        try:
            content = news_item.get("content", "")
            title = news_item.get("title", "")
            authenticity_score = news_item.get("authenticity_score", 50)
            script = script_output.get("video_script", "")

            # Calculate component scores
            tone_score = await self._calculate_tone_score(content, script)
            engagement_score = await self._calculate_engagement_score(content, script, title)
            quality_score = await self._calculate_quality_score(content, authenticity_score, script_output)

            # Overall reward (weighted average)
            reward_score = (tone_score * 0.3) + (engagement_score * 0.4) + (quality_score * 0.3)

            # Determine if correction is needed
            correction_needed = reward_score < self.reward_threshold

            feedback_data = {
                "news_item_id": news_item.get("id", ""),
                "reward_score": round(reward_score, 3),
                "tone_score": round(tone_score, 3),
                "engagement_score": round(engagement_score, 3),
                "quality_score": round(quality_score, 3),
                "correction_needed": correction_needed,
                "correction_attempts": news_item.get("correction_attempts", 0),
                "final_output": {
                    "title": title,
                    "content": content,
                    "script": script,
                    "authenticity_score": authenticity_score
                },
                "metrics": {
                    "content_length": len(content.split()),
                    "script_length": len(script.split()) if script else 0,
                    "processing_timestamp": datetime.now().isoformat(),
                    "reward_components": {
                        "tone_weight": 0.3,
                        "engagement_weight": 0.4,
                        "quality_weight": 0.3
                    }
                }
            }

            # Save feedback to database
            if db_service.database:
                await db_service.save_rl_feedback(feedback_data)

            return feedback_data

        except Exception as e:
            return {
                "error": f"Reward calculation failed: {str(e)}",
                "reward_score": 0.0,
                "correction_needed": True
            }

    async def _calculate_tone_score(self, content: str, script: str) -> float:
        """Calculate tone appropriateness score (0-1)"""
        try:
            # Analyze content tone using Uniguru sentiment analysis
            sentiment_result = await uniguru_service.analyze_sentiment(content)

            if sentiment_result.get("success"):
                polarity = sentiment_result.get("polarity", 0.0)
                # For news, we want neutral to slightly positive tone
                # Optimal polarity is between -0.1 and 0.3
                if -0.1 <= polarity <= 0.3:
                    tone_score = 0.9
                elif -0.3 <= polarity <= 0.5:
                    tone_score = 0.7
                else:
                    tone_score = 0.4
            else:
                # Fallback: keyword-based analysis
                emotional_words = ["shocking", "outrageous", "unbelievable", "devastating", "incredible"]
                neutral_words = ["according to", "reported", "stated", "confirmed", "announced"]

                emotional_count = sum(1 for word in emotional_words if word in content.lower())
                neutral_count = sum(1 for word in neutral_words if word in content.lower())

                if neutral_count >= emotional_count + 2:
                    tone_score = 0.85
                elif neutral_count >= emotional_count:
                    tone_score = 0.7
                else:
                    tone_score = 0.4

            # Check script tone consistency
            if script:
                script_emotional = sum(1 for word in emotional_words if word in script.lower())
                script_neutral = sum(1 for word in neutral_words if word in script.lower())

                if script_neutral >= script_emotional:
                    tone_score += 0.1  # Bonus for consistent neutral script
                else:
                    tone_score -= 0.1  # Penalty for inconsistent tone

            return max(0.0, min(1.0, tone_score))

        except Exception as e:
            print(f"Tone score calculation error: {e}")
            return 0.5  # Neutral fallback

    async def _calculate_engagement_score(self, content: str, script: str, title: str) -> float:
        """Calculate engagement potential score (0-1)"""
        try:
            score = 0.5  # Base score

            # Content length factor
            word_count = len(content.split())
            if word_count > 300:
                score += 0.2
            elif word_count > 150:
                score += 0.1
            elif word_count < 50:
                score -= 0.2

            # Title engagement
            if title:
                title_lower = title.lower()
                engaging_words = ["breaking", "urgent", "exclusive", "major", "crisis", "update"]
                engaging_count = sum(1 for word in engaging_words if word in title_lower)
                score += min(0.15, engaging_count * 0.05)

            # Script quality
            if script:
                script_words = len(script.split())
                if script_words > 50:
                    score += 0.15
                elif script_words > 20:
                    score += 0.1

                # Check for call-to-action phrases
                cta_phrases = ["stay tuned", "more updates", "follow for more", "breaking news"]
                cta_count = sum(1 for phrase in cta_phrases if phrase in script.lower())
                score += min(0.1, cta_count * 0.05)

            # Content freshness indicators
            time_indicators = ["today", "yesterday", "this morning", "just now", "breaking"]
            time_count = sum(1 for indicator in time_indicators if indicator in content.lower())
            score += min(0.1, time_count * 0.03)

            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"Engagement score calculation error: {e}")
            return 0.5  # Neutral fallback

    async def _calculate_quality_score(self, content: str, authenticity_score: float, script_output: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-1)"""
        try:
            score = 0.5  # Base score

            # Authenticity contribution (normalized)
            score += (authenticity_score / 100) * 0.4

            # Content structure quality
            sentences = len([s for s in content.split('.') if s.strip()])
            if sentences > 8:
                score += 0.15
            elif sentences > 4:
                score += 0.1

            # Source attribution
            attribution_indicators = ["according to", "source said", "reported by", "official statement"]
            attribution_count = sum(1 for indicator in attribution_indicators if indicator in content.lower())
            score += min(0.15, attribution_count * 0.05)

            # Script quality contribution
            script_length = script_output.get("script_length", 0)
            if script_length > 30:
                score += 0.1
            elif script_length > 15:
                score += 0.05

            # Fact vs opinion balance
            opinion_words = ["i think", "in my opinion", "probably", "maybe", "could be"]
            fact_words = ["confirmed", "verified", "data shows", "research indicates", "according to"]

            opinion_count = sum(1 for word in opinion_words if word in content.lower())
            fact_count = sum(1 for word in fact_words if word in content.lower())

            if fact_count > opinion_count:
                score += 0.1
            elif opinion_count > fact_count + 2:
                score -= 0.1

            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"Quality score calculation error: {e}")
            return 0.5  # Neutral fallback

    async def check_correction_needed(self, feedback_result: Dict[str, Any]) -> bool:
        """Check if content needs correction based on reward score"""
        reward_score = feedback_result.get("reward_score", 0)
        correction_attempts = feedback_result.get("correction_attempts", 0)

        return reward_score < self.reward_threshold and correction_attempts < self.max_correction_attempts

    async def trigger_correction(self, news_item: Dict[str, Any], feedback_result: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger correction process for low-quality content"""
        try:
            news_item_id = news_item.get("id", "")
            current_attempts = news_item.get("correction_attempts", 0)

            if current_attempts >= self.max_correction_attempts:
                return {
                    "correction_triggered": False,
                    "reason": "Maximum correction attempts reached",
                    "attempts": current_attempts
                }

            # Increment correction attempts
            new_attempts = current_attempts + 1

            # Update news item
            update_data = {
                "correction_attempts": new_attempts,
                "status": "correction_pending",
                "last_correction_attempt": datetime.now().isoformat()
            }

            if db_service.database:
                await db_service.update_news_item(news_item_id, update_data)

            # Trigger re-summarization via Uniguru
            content = news_item.get("content", "")
            if content:
                # Request improved summarization
                summary_result = await uniguru_service.summarize_text(
                    content,
                    max_length=200,
                    style="concise"
                )

                if summary_result.get("success"):
                    improved_summary = summary_result.get("summary")

                    # Generate new script with improved content
                    script_task_data = {
                        "title": news_item.get("title", ""),
                        "content": content,
                        "summary": improved_summary
                    }

                    script_result = await agent_registry.submit_task("script_agent", script_task_data)

                    return {
                        "correction_triggered": True,
                        "attempts": new_attempts,
                        "improved_summary": improved_summary,
                        "new_script_task_id": script_result,
                        "correction_method": "uniguru_resummarization"
                    }

            return {
                "correction_triggered": False,
                "reason": "Unable to generate improved content",
                "attempts": new_attempts
            }

        except Exception as e:
            return {
                "correction_triggered": False,
                "error": f"Correction trigger failed: {str(e)}"
            }

    async def get_feedback_metrics(self, news_item_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Get feedback metrics and statistics"""
        try:
            if not db_service.database:
                return {"error": "Database not connected"}

            if news_item_id:
                # Get feedback for specific news item
                feedback_list = await db_service.get_feedback_by_news_item(news_item_id)
            else:
                # Get recent feedback from all items
                collection = await db_service.get_collection("rl_feedback")
                cursor = collection.find().sort("created_at", -1).limit(limit)
                feedback_list = await cursor.to_list(length=limit)

            if not feedback_list:
                return {"total_feedback": 0, "metrics": {}}

            # Calculate aggregate metrics
            total_feedback = len(feedback_list)
            avg_reward = sum(f.get("reward_score", 0) for f in feedback_list) / total_feedback
            avg_tone = sum(f.get("tone_score", 0) for f in feedback_list) / total_feedback
            avg_engagement = sum(f.get("engagement_score", 0) for f in feedback_list) / total_feedback
            avg_quality = sum(f.get("quality_score", 0) for f in feedback_list) / total_feedback

            corrections_needed = sum(1 for f in feedback_list if f.get("correction_needed", False))
            correction_rate = corrections_needed / total_feedback if total_feedback > 0 else 0

            # Score distribution
            score_ranges = {
                "excellent": sum(1 for f in feedback_list if f.get("reward_score", 0) >= 0.8),
                "good": sum(1 for f in feedback_list if 0.6 <= f.get("reward_score", 0) < 0.8),
                "needs_improvement": sum(1 for f in feedback_list if 0.4 <= f.get("reward_score", 0) < 0.6),
                "poor": sum(1 for f in feedback_list if f.get("reward_score", 0) < 0.4)
            }

            return {
                "total_feedback": total_feedback,
                "metrics": {
                    "average_reward_score": round(avg_reward, 3),
                    "average_tone_score": round(avg_tone, 3),
                    "average_engagement_score": round(avg_engagement, 3),
                    "average_quality_score": round(avg_quality, 3),
                    "correction_rate": round(correction_rate, 3),
                    "score_distribution": score_ranges
                },
                "recent_feedback": feedback_list[:10],  # Last 10 feedback entries
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Metrics retrieval failed: {str(e)}"}

# Global instance
rl_feedback_service = RLFeedbackService()