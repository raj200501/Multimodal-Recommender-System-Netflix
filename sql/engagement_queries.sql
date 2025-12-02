-- Daily active users and average completion
SELECT DATE_TRUNC('day', timestamp) AS day, COUNT(DISTINCT user_id) AS dau, AVG(completion_ratio) AS avg_completion
FROM fact_views
GROUP BY day
ORDER BY day;

-- Top devices by watch time
SELECT device_type, SUM(watch_time_minutes) AS total_watch_minutes
FROM fact_views
GROUP BY device_type
ORDER BY total_watch_minutes DESC;

-- Recommendation coverage by model
SELECT model, COUNT(DISTINCT user_id) AS users_covered, COUNT(*) AS total_rows
FROM recommendations
GROUP BY model;
