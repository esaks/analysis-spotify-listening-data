# analysis-spotify-listening-data
Personal project analyzing Spotify music listening data

## Project Summary
As a regular music listener, I wanted to better understand my listening habits. I retrieved my personal data from Spotify, a dataset of around 11,000 songs listened to in the last year. I queried the Spotify API for the id numbers of as many unique songs as I could get, and then the Reccobeats API for audio features of those songs. I created relational tables in postgreSQL and then generated visualizations in Tableau showing listening trends over time, and top artists/songs. Since this project used my personal data, I did not include the dataset in the repository.

## Purpose
I wanted to gain more experience working with querying APIs, and larger datasets. I also wanted to practice postgreSQL and Tableau.

## Example Output
<img width="483" height="390" alt="monthly listening trend graph" src="https://github.com/user-attachments/assets/229a068a-4426-473c-962b-1511b6924d4d" />

## Acknowledgements
I consulted various web resources in completing this project. 
These include:

<strong>Inspiration</strong>
* Romanowski, Jakub. "Make Your Own Spotify Wrapped with SQL (Because Why Not?), <i>LearnSQL Blog</i>
* D, Marcus. "How I Analysed My Spotify Data Using SQL and Python", <i>Medium</i>
  
<strong>Tutorials and Resources</strong>
* Alex the Analyst. "Installing and Creating Database in PostgreSQL." <i>Youtube.</i>
* Alex the Analyst. "How to Install Tableau and Create First Visualization | Tableau Tutorial for Beginners." <i>Youtube.</i>
* Moesl, Thomas. "SQL Challenge #6: Identify Top Sellers by Product Category", <i>Medium</i>
  
<strong>ChatGPT</strong>
* Used to find the appropriate API to query
* Used for debugging and formatting suggestions

