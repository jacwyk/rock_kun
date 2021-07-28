# rock_kun
Discord study log level system bot




Basic overview: 
-Log in study session start and end times to earn XP for every 60 minutes study time
-XP will allow you to level up
-Special roles available as levels increase
-Leaderboard and ranking of all members in the server
-The study time recorded in total can also be viewed




Instructions/Commands:
-Record study session start and end time using command: 
**!studying (start hr) (start min) (end hr) (end min)**
  Ex: **!studying 09 31 14 12** for study session 09:31am-2:12pm
  Note: space between each set of numbers required for session to be recorded (ex: **!studying 3.01-6.39** will not work)
  Note: everything must be filled in, ie. command input must have start hr, start min, end hr, end min (ex: **!studying 9 50 10 03** will work, but **!studying 9 10 03** will not)
  Note: if going from am to pm, use 24hr time instead of 12hr. Otherwise, 12/24 both fine (ex: for 7pm-8pm, **!studying 7 00 8 00** and **!studying 19 00 20 00** will both work)
  Note: end time must be greater than start time to be recorded (ex: 10:25pm to 1:05am must be separated into 2 sessions, **!studying 10 25 12 00** and **!studying 12 00 1 05**)
  
-Check personal stats using command:
**!stats**
  This shows your current: level, XP, Rank, Level Progress (% to the next level), Study Time (total study time logged in days, hrs, mins) 
  
-Check leaderboard using command:
**!leaderboard**
  Reactions to change pages





Future edit notes:
-auto count study time when joining discord library vc (...?)
-depending on usage, clear out database every month/sem (...?)
-when !studying command used without time input, auto take in timecode of msg sent to be start/end time 
-separate start and stop time command

