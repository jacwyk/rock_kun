# rock_kun
Discord study log level system bot




Basic overview: <br />
-Log in study session start and end times to earn XP for every 60 minutes study time <br />
-XP will allow you to level up <br />
-Special roles available as levels increase <br />
-Leaderboard and ranking of all members in the server <br />
-The study time recorded in total can also be viewed <br />




Instructions/Commands: <br />
-Record study session start and end time using command: <br />
**!studying (start hr) (start min) (end hr) (end min)** <br />
  Ex: **!studying 09 31 14 12** for study session 09:31am-2:12pm <br />
  Note: space between each set of numbers required for session to be recorded (ex: **!studying 3.01-6.39** will not work) <br />
  Note: everything must be filled in, ie. command input must have start hr, start min, end hr, end min (ex: **!studying 9 50 10 03** will work, but **!studying 9 10 03** will not) <br />
  Note: if going from am to pm, use 24hr time instead of 12hr. Otherwise, 12/24 both fine (ex: for 7pm-8pm, **!studying 7 00 8 00** and **!studying 19 00 20 00** will both work) <br />
  Note: end time must be greater than start time to be recorded (ex: 10:25pm to 1:05am must be separated into 2 sessions, **!studying 10 25 12 00** and **!studying 00 00 1 05**) <br />
  
-Check personal stats using command: <br />
**!stats** <br />
  This shows your current: level, XP, Rank, Level Progress (% to the next level), Study Time (total study time logged in days, hrs, mins) <br />
  
-Check leaderboard using command: <br />
**!leaderboard** <br />
  Reactions to change pages <br />





Future edit notes: <br />
-auto count study time when joining discord library vc (...?) <br />
-depending on usage, clear out database every month/sem (...?) <br />
-when !studying command used without time input, auto take in timecode of msg sent to be start/end time <br />
-separate start and stop time command <br />

