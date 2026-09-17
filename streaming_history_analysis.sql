--Analyze Spotify data

--General streaming history
CREATE TABLE IF NOT EXISTS streaming_history (
    endTime TIMESTAMP,
    artistName VARCHAR(255),
    trackName VARCHAR(255),
    msPlayed INT
);

--Get first 10 rows 
SELECT * from streaming_history LIMIT 10;

--Top 10 Most played tracks
CREATE OR REPLACE VIEW top_tracks AS
SELECT trackname, artistname, SUM(msplayed)/60000 AS totalminutes
FROM streaming_history
GROUP BY trackname, artistname
ORDER BY totalminutes DESC --sorts in descending order by minutes
LIMIT 10;

--Top 10 Artists
CREATE OR REPLACE VIEW  top_artists AS
SELECT artistname, SUM(msplayed)/60000 AS totalminutes
FROM streaming_history
GROUP BY artistname
ORDER BY totalminutes DESC
LIMIT 10;

--Monthly listening time
CREATE OR REPLACE VIEW monthly_listening_trend AS
SELECT DATE_TRUNC('month', endTime) AS month, SUM(msPlayed) / 3600000 AS hours
FROM streaming_history
GROUP BY month
ORDER BY month;

--Top song every month
CREATE OR REPLACE VIEW monthly_top_songs AS
WITH monthly_ranked_songs AS (
SELECT 
	DATE_TRUNC('month', endTime) AS month, 
	trackname, 
	SUM(msplayed)/60000 AS minutes_played, 
DENSE_RANK() OVER(
	PARTITION BY DATE_TRUNC('month', endTime)
	ORDER BY SUM(msplayed)/60000 DESC 
	) AS rank
FROM streaming_history
GROUP BY month, trackname
)
SELECT 
	month,
	trackname,
	minutes_played
FROM monthly_ranked_songs
WHERE rank = 1
ORDER BY month;

--Analysis with audio track features
--Create table
CREATE TABLE IF NOT EXISTS spotify_data (
    endTime TIMESTAMP,
    artistName VARCHAR(255),
    trackName VARCHAR(255),
    msPlayed INT,
	track_id VARCHAR(255),
	tempo NUMERIC,
	energy NUMERIC,
	danceability NUMERIC,
	valence NUMERIC,
	acousticness NUMERIC,
	instrumentalness NUMERIC, 
	liveness NUMERIC, 
	loudness NUMERIC,
	speechiness NUMERIC
);

