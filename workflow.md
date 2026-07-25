# Medieval Market Tycoon (CLI) — Development Workflow

This roadmap is designed as if you were building a professional simulation game. Every phase produces a playable version while laying the foundation for the next systems.

---

# Phase 0 — Project Foundation

**Goal**

Create a scalable architecture before writing gameplay.

## Tasks

* Initialize project
* Setup Git repository
* Create folder structure
* Create game loop
* Implement logging
* Implement configuration system
* Implement save directory

```
project/
│
├── assets/
├── data/
├── saves/
├── src/
│   ├── core/
│   ├── world/
│   ├── economy/
│   ├── player/
│   ├── npc/
│   ├── ui/
│   ├── events/
│   ├── systems/
│   └── utils/
│
├── main.py
└── README.md
```

---

# Phase 1 — Core Engine

**Goal**

The game can start, load, save, and advance time.

## Build

* Main Menu
* New Game
* Save
* Load
* Exit
* Tick System
* Command Parser

Workflow

```
Launch Game
      │
      ▼
 Main Menu
      │
      ▼
 Create World
      │
      ▼
 Game Loop
      │
      ▼
 Read Command
      │
      ▼
 Execute
      │
      ▼
 Update Systems
      │
      ▼
 Render Screen
```

---

# Phase 2 — World Generation

Generate the entire kingdom.

## Build

* Kingdom Name
* Town Name
* Population
* Starting Gold
* Initial Market
* Initial NPCs
* Initial Buildings
* Calendar

Example

```
Kingdom
-------------------
Name        Ashvale
Population  530
Season      Spring
Weather     Sunny
Treasury    $1,500
```

---

# Phase 3 — Calendar & Time System

Everything depends on time.

## Build

```
Year

Season

Month

Week

Day
```

Command

```
next
```

Every day automatically updates:

* economy
* production
* NPC behavior
* events
* weather

---

# Phase 4 — Data Database

Create JSON databases.

```
items.json

buildings.json

jobs.json

npc_traits.json

weather.json

events.json

recipes.json
```

Everything should be data-driven.

Never hardcode prices or buildings.

---

# Phase 5 — Economy Engine

This is the heart of the game.

Each item stores

```
Name

Base Price

Supply

Demand

Current Price

Production Rate

Consumption Rate
```

Price Formula

```
Supply ↑

↓

Price ↓


Demand ↑

↓

Price ↑
```

Example

```
Market

Bread      $12 (+2)

Iron       $46 (-4)

Wine       $71 (+8)

Salt       $18 (-1)
```

---

# Phase 6 — Inventory System

Build

```
Player Inventory

Warehouse

Gold

Weight

Capacity
```

Commands

```
inventory

warehouse

deposit

withdraw
```

---

# Phase 7 — Trading System

Commands

```
buy

sell

inspect

market
```

Example

```
buy bread 20

sell iron 5
```

Workflow

```
Player

↓

Validate Gold

↓

Validate Stock

↓

Complete Transaction

↓

Update Economy
```

---

# Phase 8 — Building System

Player can construct buildings.

Examples

```
Bakery

Blacksmith

Farm

Warehouse

Fish Market

Tavern

Stable

Lumber Mill
```

Each building stores

```
Level

Workers

Maintenance

Output

Efficiency
```

---

# Phase 9 — Production System

Buildings automatically produce goods.

Example

```
Farm

↓

Produces Wheat

↓

Bakery

Consumes Wheat

↓

Produces Bread

↓

Market

Sells Bread
```

Everything runs automatically each day.

---

# Phase 10 — NPC System

Generate merchants.

NPC attributes

```
Name

Age

Profession

Gold

Inventory

Mood

Loyalty

Greed

Reputation

Relationship
```

NPC professions

```
Farmer

Miner

Merchant

Hunter

Blacksmith

Carpenter

Fisherman

Brewer
```

---

# Phase 11 — Workforce

Allow hiring workers.

```
hire

fire

payroll
```

Worker stats

```
Skill

Experience

Morale

Health

Salary
```

Higher skill

↓

Higher production

---

# Phase 12 — Supply Chain

Goods move through the economy.

```
Forest
      │
      ▼
Lumber Mill
      │
      ▼
Warehouse
      │
      ▼
Market
      │
      ▼
Citizens
```

If one link fails

↓

Entire chain slows down.

---

# Phase 13 — Citizens Simulation

Citizens consume resources.

Needs

```
Food

Clothing

Tools

Housing

Luxury
```

If food runs out

```
Population Happiness ↓

Crime ↑

Demand ↑

Migration ↑
```

---

# Phase 14 — Weather & Seasons

Weather affects production.

Examples

```
Sunny

Rain

Storm

Snow

Heatwave
```

Season effects

```
Winter

Wood +60%

Food +35%

Flowers -90%
```

---

# Phase 15 — Random Events

Daily event generator.

Examples

```
Fire

Bandits

Festival

Disease

Merchant Caravan

Royal Visit

Mine Collapse

Harvest
```

Each event changes simulation variables.

---

# Phase 16 — Reputation System

Track player's influence.

Ranks

```
Unknown Merchant

Trader

Guild Member

Guild Master

Royal Supplier

Merchant Lord
```

Higher reputation unlocks

* better NPCs
* cheaper prices
* royal contracts
* exclusive items

---

# Phase 17 — Town Expansion

Town evolves automatically.

```
Village

↓

Hamlet

↓

Town

↓

City

↓

Trade Capital
```

Expansion unlocks

* new buildings
* more citizens
* higher demand
* new industries

---

# Phase 18 — Multi-Town Economy

Generate neighboring towns.

Example

```
Ashvale

Riverhold

Stoneford

Westport
```

Each town has

* unique prices
* different resources
* different demand

This creates arbitrage opportunities.

---

# Phase 19 — Caravan System

Transport goods.

```
Warehouse

↓

Caravan

↓

Travel

↓

Destination

↓

Sell Goods
```

Possible outcomes

```
Successful

Delayed

Ambushed

Broken Wagon

Lost Cargo
```

---

# Phase 20 — Politics & Kingdom

Kingdom-wide simulation.

Systems

```
Taxes

Royal Orders

Trade Laws

Guild Policies

Wars

Embargoes
```

Example

```
King increases taxes

↓

Citizen spending decreases

↓

Market revenue decreases
```

---

# Phase 21 — Advanced Economy

Introduce macroeconomics.

Features

* Inflation
* Deflation
* Monopolies
* Black Market
* Imports
* Exports
* Resource Scarcity
* Economic Crisis
* Merchant Competition

---

# Phase 22 — AI Competitors

Independent merchant companies.

Each AI

* buys goods
* builds shops
* hires workers
* expands
* competes for profit

The world continues evolving even if the player does nothing.

---

# Phase 23 — Endgame

Late-game objectives.

Become

```
Local Merchant

↓

Guild Master

↓

Royal Treasurer

↓

Minister of Commerce

↓

Merchant Prince

↓

Merchant King
```

Unlock

* national trade routes
* taxation
* diplomacy
* kingdom management

---

# Phase 24 — Polish

Improve the player experience.

Features

* Command history
* Auto-completion
* Colored CLI output
* ASCII tables
* Progress bars
* Sound effects (terminal bell)
* Statistics dashboard
* Achievement system
* Save compression
* Performance optimization

---

# Final Architecture

```
                         Game Engine
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
     Command Parser      Save Manager      Render Engine
          │
          ▼
     Simulation Engine
          │
 ┌────────┼────────┬────────┬────────┬─────────┐
 ▼        ▼        ▼        ▼        ▼         ▼
World   Economy   NPCs   Buildings Citizens Events
 │        │        │        │        │         │
 └────────┴────────┴────────┴────────┴─────────┘
                     │
                     ▼
              Daily Tick System
                     │
                     ▼
              Terminal Interface
```

## Recommended Milestones

| Milestone        | Playable Features                                             |
| ---------------- | ------------------------------------------------------------- |
| **MVP v0.1**     | Menu, save/load, calendar, market, buy/sell                   |
| **Alpha v0.2**   | Buildings, production, inventory, warehouse                   |
| **Alpha v0.3**   | NPCs, workers, dynamic pricing, supply chains                 |
| **Beta v0.4**    | Weather, seasons, random events, reputation                   |
| **Beta v0.5**    | Multi-town trading, caravans, AI competitors                  |
| **Release v1.0** | Politics, advanced economy, endgame progression, achievements |

This workflow follows a common simulation-game development pattern: **Core Engine → Simulation Systems → Economy → Automation → World Expansion → Endgame**. It minimizes refactoring while keeping every milestone playable and making future systems easy to integrate.
