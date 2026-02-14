# Expected Value (EV) — How It Works

## What is EV?

EV = **expected cups removed per shot attempt**. Higher is better. It answers: *"When I step up to the table, what's my best play?"*

---

## Individual Shot EV (without 2B1C)

### Normal

$$EV_{\text{normal}} = \frac{\text{normal\_hits}}{\text{normal\_total}}$$

A normal hit removes 1 cup. EV is just the hit rate.

### Bounce

$$EV_{\text{bounce}} = \frac{\sum_{i \in \text{bounce hits}} (b_i + 1)}{\text{bounce\_total}}$$

A bounce hit removes $b + 1$ cups, where $b$ is the number of bounces. A single-bounce hit removes 2 cups, a double-bounce removes 3, etc. We sum the actual cups removed across all bounce hits and divide by total bounce attempts.

### Trickshot

$$EV_{\text{trick}} = \frac{\text{trickshot\_hits}}{\text{trickshot\_total}}$$

A trickshot hit removes 1 cup. Same as normal — just the hit rate. Note: trickshots are imposed (ball reclaimed), not a strategic choice.

---

## 2 Balls 1 Cup (2B1C)

### What is it?

When both teammates hit the **same cup** in the same round, it removes **3 cups** instead of 2. That's a **+1 bonus cup** over two independent hits on different cups.

### How we estimate the probability

We don't count actual 2B1C events (too rare for reliable stats). Instead, we predict the probability using each player's accuracy and cup targeting patterns.

#### Step 1 — Teammate's hit rate

$$p_B = \frac{\text{teammate's hits}}{\text{teammate's total shots}}$$

#### Step 2 — Cup targeting distributions

From the cup heatmap, we know how often each player hits each cup position. We convert this to a probability distribution — *given that the player hits, which cup do they hit?*

$$q_A(c) = \frac{\text{player A's hits on cup } c}{\text{player A's total hits}}$$

$$q_B(c) = \frac{\text{player B's hits on cup } c}{\text{player B's total hits}}$$

#### Step 3 — Overlap (dot product)

The probability that both players target the same cup, given both hit, is the dot product of their cup distributions:

$$\text{overlap} = \sum_{c} q_A(c) \cdot q_B(c)$$

If both players always aim at the same cup, overlap = 1. If they spread evenly across 6 cups, overlap ≈ 0.167.

#### Step 4 — 2B1C probability

$$P(\text{2B1C}) = p_B \times \text{overlap}$$

This is the probability that, given player A hits some cup, player B also hits that same cup in the same round.

---

## Full EV (with 2B1C)

The 2B1C bonus adds expected cups to every hit. If player A hits a cup, there's a $P(\text{2B1C})$ chance the team gets 1 extra cup from the overlap. So the full EV per attempt is:

$$EV = \frac{\text{cups removed per hit}}{\text{attempts}} \times (1 + P(\text{2B1C}))$$

Expanded for each shot type:

$$EV_{\text{normal}} = \frac{\text{normal\_hits}}{\text{normal\_total}} \times (1 + p_B \cdot \text{overlap})$$

$$EV_{\text{bounce}} = \frac{\sum_{i \in \text{bounce hits}} (b_i + 1)}{\text{bounce\_total}} \times (1 + p_B \cdot \text{overlap})$$

$$EV_{\text{trick}} = \frac{\text{trickshot\_hits}}{\text{trickshot\_total}} \times (1 + p_B \cdot \text{overlap})$$

---

## Example

Player A: 40% normal hit rate, teammate B: 35% hit rate, overlap = 0.25.

$$P(\text{2B1C}) = 0.35 \times 0.25 = 0.0875$$

$$EV_{\text{normal}} = 0.40 \times (1 + 0.0875) = 0.40 \times 1.0875 = 0.435$$

Without 2B1C, EV would be 0.40. The teammate synergy adds 0.035 cups per attempt.

Now if A has a bounce hit rate of 50% with average 1 bounce (2 cups per hit):

$$EV_{\text{bounce}} = \frac{2 \times \text{bounce\_hits}}{\text{bounce\_total}} \times 1.0875 = 1.0 \times 1.0875 = 1.0875$$

Bounce EV (1.09) vs Normal EV (0.44) → **bouncing is 2.5× more valuable**.

---

## Assumptions

- Each player shoots independently at a random cup following their historical distribution
- Cup targeting doesn't change based on remaining cups (we use tournament-wide heatmap averages)
- Teams are fixed throughout the tournament, so each player has exactly one teammate
- 2B1C probability is a prediction, not a count of actual 2B1C events
