# Project Charter — Team [18]

## Project title
Casino Night

## Description
A Python web application backed by a MySQL database where registered 
players log in, hold a virtual currency balance, and bet it on simple 
games. Players can see a leaderboard ranking everyone by balance. It is for 
classmates and friends who want a low-stakes game with a bit of competition.

## Objectives and goals
1. A new user can register and log in with a username and password. 
Passwords are stored hashed, and every page except login and register 
requires a session.
2. New accounts start with $1000. Each account receives $200 once per 
calendar day, verified by an automated test that simulates two consecutive 
days and a repeat claim on the same day.
3. All games are playable end to end with betting. A balance never 
goes below $0, and every bet settlement updates both players’ balances in a 
single database transaction.
4. The leaderboard shows the top 5 players and loads in under three seconds 
with 50 players in the database.
5. Multiplayer bets are matched correctly. Two players whose bets differ by 
more than $100 are rejected, and otherwise the wager is the average of the 
two.

## Scope

**In scope**
- Registration, login, logout
- Balance, starting grant, and daily bonus
- Rock paper scissors (multiplayer/singleplayer), slots (singleplayer) 
and blackjack (singleplayer)
- Betting and settlement
- Leaderboard
- MySQL schema hosted on Aiven

**Out of scope**
- Real money, payments, or anything resembling actual gambling
- Password reset by email, social login, profile pictures
- Chat, friends lists, spectating
- Admin dashboard

## Definition of done
- It is merged to main through a merge request.
- Its tests, which are written by someone not writing the code, pass.
- Someone who did not write it has reviewed and approved it.
- Any money-handling code has a test covering the edge cases: insufficient 
funds, a tie, and a bet mismatch.
- The application is tested on at least two people’s laptop.

## Team and roles
| Member | GitLab userid | Role this sprint (1) |
| Cedric | @z2964wan1 | developer |
| Daniel | @dadoga1 | developer |
| Fei | @f252zhan1 | developer |
| Kelly | @k26du1 | Scrum master |
| Isaac | @i9lu1 | Product owner |

## Assumptions
- Everyone can run Python and MySQL locally, or connect to a shared hosted 
database.
- A free-tier hosted MySQL is enough for our data volume.
- We use one Python web framework, Flask.
- “Midnight” means one fixed timezone, EST, not each player’s 
local time.
- The multiplayer games need two players online at the same time.
- We can call outside the lab slot at least once a week.

## Constraints
- Fixed term deadlines.
- Five developers with mixed experience in web and database work.
- Free-tier hosting and no budget.
- Have to stay within scope and not do anything out of scope. 

## Risks
| Risk | How likely | How bad | What we will do about it |
| Scope too large (three games, multiplayer, and betting) | Likely | Severe | Reduce: plan for about half. Slots and single-player RPS come first; multiplayer and the third game are stretch goals. The out-of-scope list lets us say no. |
| Integration left to the end (login, database, betting, and games built separately) | Likely | Severe | Reduce: build an end-to-end skeleton in sprint 1 (register, log in, see balance, place one bet) on the shared deployed site. |
| A member disengages | Possible | Severe | Reduce: keep the board live, flag problems early at standups, and never let one person own a critical module alone. |
| Team database unavailable (free tier down or credentials lost) | Possible | Moderate | Reduce: keep the schema and seed script in the repository so anyone can recreate the database locally. |
| Multiplayer sync is harder than expected (matching players, hiding choices until both submit, handling a player who leaves) | Likely | Moderate | Reduce: build single-player first; keep multiplayer to simple turn submission by polling, with a timeout that forfeits the bet. |

## Sign-off
We have read this charter and agree to it.
Isaac Lu, Daniel Adoga, Kelly Du, Fei Zhang, Cedric Wang Date: 2026-11-05
