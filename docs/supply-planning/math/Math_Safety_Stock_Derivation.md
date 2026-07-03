<!-- MIRROR: auto-synced from notes/math/supply-planning/Math_Safety_Stock_Derivation.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: math-safety-stock-derivation
type: math_domain
status: draft
dependencies:
tags: []
invariants:
  - id: rop-formula
    statement: "Reorder point ROP = E[DDLT] + SS for valid inputs"
  - id: ss-formula
    statement: "Safety stock SS = Z x sigma_DDLT given valid demand and lead-time distributions"
---
# Safety Stock Derivation

Formal derivation of Demand During Lead Time (DDLT), safety stock ($SS$), and reorder point ($ROP$) from first principles. This note supplies the **Layer 1** probability model for supply-planning engines such as the [MRP Pipeline](../../../../Notes/projects/mrp/README.md); the [Alpha/Beta/Delta](../../../../Notes/projects/mrp/README.md) proposition isolates variance in the simulation.

**Layer 4 invariants:** The MRP engine should enforce $ROP = E[DDLT] + SS$ and $SS = Z \times \sigma_{DDLT}$ given valid inputs. Flag: verify `mrp_pipeline` tests/schemas cover these formulas when implementation matures.

See also [OR_AI_ASI.md](../../../../Notes/meta/OR_AI_ASI.md) for OR pillar context (state space, constraints, objective function) and [Layer4_TypeB_Auditing.md](../../../../Notes/meta/Layer4_TypeB_Auditing.md) for conservation and state-machine invariants.

## Part 1: The Foundation of Chaos

Before we calculate risk, we have to translate the messy physical world into usable numbers.

### 1. The Random Variable ($X$)

A random variable is not actually random; it is a strict, measurable function that maps abstract physical states from a sample space ($\Omega$) to real numbers ($\mathbb{R}$).

- **Formula:** $X: \Omega \rightarrow \mathbb{R}$
- **Dice Example:** $\Omega$ is the physical tumbling of plastic. $X$ is the function that maps that tumbling to a discrete integer.
  - **Demand ($D$):** Modeled as a **d6** (outcomes 1 through 6).
  - **Lead Time ($L$):** Modeled as a **d10** (outcomes 1 through 10).

### 2. Expected Value ($E[X]$ or $\mu$)

The center of mass of your probability distribution. It is the weighted average of all possible outcomes.

- **Formula:** $E[X] = \sum x_i P(x_i)$
- **Dice Example:**
  - Average Demand ($\mu_D$): $E[d6] = 3.5$ units.
  - Average Lead Time ($\mu_L$): $E[d10] = 5.5$ days.

## Part 2: The Geometry of Risk ($L^2$ Hilbert Space)

To measure risk, we must look at how far outcomes deviate from our Expected Value. We do this inside an $L^2$ Hilbert space, which allows us to treat random variables as geometric vectors.

### 1. Variance ($Var(X)$ or $\sigma^2$)

The Expected Value of the squared differences from the mean. We square it to heavily penalize outliers and to ensure the function is smooth and differentiable for optimization.

- **Formula:** $Var(X) = E[(X - E[X])^2]$
- **Dice Example:**
  - Demand Variance ($\sigma_D^2$): $\approx 2.917$
  - Lead Time Variance ($\sigma_L^2$): $8.25$

### 2. Standard Deviation ($\sigma$)

The **Root Mean Square** distance from the mean. Taking the square root of the variance pulls the math back down into our original units (e.g., from "squared days" back to "days"). Geometrically, this is the $L^2$ norm (the "length") of our mean-centered vector.

- **Formula:** $\sigma_X = \sqrt{Var(X)}$
- **Dice Example:**
  - Demand Risk ($\sigma_D$): $\sqrt{2.917} \approx 1.71$ units.
  - Lead Time Risk ($\sigma_L$): $\sqrt{8.25} \approx 2.87$ days.

### 3. Covariance ($Cov(X,Y)$) & Correlation ($\rho$)

Covariance is the inner product of two risk vectors in our Hilbert space. It measures how two variables move together. Correlation ($\rho$) is that inner product scaled down to a strict range between $-1.0$ and $1.0$.

- **Formulas:**
  - $Cov(X,Y) = E[(X - E[X])(Y - E[Y])]$
  - $\rho = \frac{Cov(X,Y)}{\sigma_X \sigma_Y}$
- **Dice Example:** The d6 and the d10 do not physically affect each other. Therefore, their Covariance is **0**. In $L^2$ space, an inner product of 0 means the vectors are perfectly **orthogonal** (at a 90-degree angle).

## Part 3: Combining Independent Risks

When we combine two random variables, we must calculate the variance of their sum.

### 1. The General Addition Rule

- **Formula:** $Var(X+Y) = Var(X) + Var(Y) + 2Cov(X,Y)$

### 2. The Pythagorean Theorem of Risk

Because our Demand (d6) and Lead Time (d10) are independent ($\rho = 0$), the $2Cov(X,Y)$ term completely drops out. To find the total standard deviation, we use the Pythagorean theorem to calculate the hypotenuse of the two orthogonal vectors.

- **Formula:** $\sigma_{X+Y} = \sqrt{\sigma_X^2 + \sigma_Y^2}$
- **Dice Example:** If we roll the d6 and d10 together, the standard deviation of their sum is *not* $1.71 + 2.87 = 4.58$ (which would imply 100% correlation). Independent risks offset each other. The true combined risk is $\sqrt{2.917 + 8.25} \approx 3.34$.

## Part 4: The Compound Random Variable (DDLT)

In supply planning, we are not just adding one day of Demand to one day of Lead Time. Lead Time dictates *how many times* we roll the Demand die.

### 1. Demand During Lead Time ($DDLT$)

A Random Sum of Random Variables.

- **Formula:** $DDLT = \sum_{i=1}^{L} D_i$
- **Dice Example:** You roll the d10 once (Supplier). If it lands on 4, you must draw exactly four d6s (Customers) and roll them all. The sum of those four d6s is your $DDLT$.

### 2. Wald's Equation (The Expected Value)

The absolute baseline of inventory consumed while waiting for a truck.

- **Formula:** $E[DDLT] = \mu_L \times \mu_D$
- **Dice Example:** On average, the d10 rolls a 5.5. On average, each d6 rolls a 3.5. Your average pipeline consumption is $5.5 \times 3.5 = 19.25$ units.

### 3. Eve's Law / Law of Total Variance

Because the upper limit of our summation ($L$) is random, the variance splits into two perfectly orthogonal blocks.

- **Formula:** $Var(DDLT) = (\mu_L \sigma_D^2) + (\mu_D^2 \sigma_L^2)$

## Part 5: The Culmination — The Safety Stock Formula

Safety Stock ($SS$) is the extra inventory required to absorb the standard deviation of Demand During Lead Time, scaled by how aggressively you want to protect your service level ($Z$).

$$SS = Z \times \sqrt{\mu_L \sigma_D^2 + \mu_D^2 \sigma_L^2}$$

**The Formula Translated into the Dice Game:**

The square root is the Pythagorean hypotenuse wrapping around two completely independent threats:

1. **The "Crazy Customer" Risk ($\mu_L \sigma_D^2$):** Your supplier is perfect (d10 rolls average every time). However, you are exposed to the natural chaos of the d6s. You take the variance of the d6 ($\sigma_D^2$) and multiply it by the average number of days you are forced to play the game ($\mu_L$).
2. **The "Broken Truck" Risk ($\mu_D^2 \sigma_L^2$):** Your customers are perfect robots (always buying exactly $\mu_D$). But the supplier is chaotic. Every time the d10 rolls one integer higher, it forces you to bleed an entire average day of demand. You take the variance of the d10 ($\sigma_L^2$) and heavily scale it by the square of that daily average ($\mu_D^2$).

### 1. The Z-Score ($Z$)

A $Z$-score is simply a multiplier. It dictates exactly **how many standard deviations away from the mean** you want to establish your boundary.

- **Formula:** $Z = \frac{X - \mu}{\sigma}$ (where $X$ is your chosen boundary).
- **Dice Example:** If your Expected Value ($\mu$) is 15, and your standard deviation ($\sigma$) is 5, drawing a boundary at 20 means you are exactly $1.0$ standard deviation away from the mean. Your $Z$-score is $1.0$.

### 2. Cycle Service Level (The Win Rate)

In supply planning, the $Z$-score directly translates to your "Cycle Service Level"—the mathematical probability of not running out of stock while waiting for the truck.

- **$Z = 0$ (50% Win Rate):** You cover $0$ standard deviations. You only survive the exact average and below-average outcomes.
- **$Z = 1.0$ (84.1% Win Rate):** You cover $1$ standard deviation away from the mean.
- **$Z = 2.0$ (97.7% Win Rate):** You cover $2$ standard deviations away from the mean.

### 3. The Non-Linear Cost of Certainty

Because the Bell Curve has long, thin tails, moving further away from the mean becomes exponentially more expensive. Moving from 84% to 97% certainty requires buying one standard deviation of inventory. Pushing from 97% to the physics-level 99.999% requires buying almost three additional standard deviations of inventory to cover mathematically microscopic risks.

## Part 7: The Safety Stock Synthesis

This is the culmination of the entire system. When you strip away the business jargon, Safety Stock is literally just a mathematical instruction: *"March $Z$ standard deviations to the right of the mean."*

### 1. The Anchor: Expected Demand During Lead Time ($E[DDLT]$)

Before you can march away from the mean, you have to find it. This is your baseline pipeline inventory.

- **Formula:** $E[DDLT] = \mu_L \times \mu_D$
- **In English:** The exact average number of units your customers will buy while you wait for the exact average delivery truck.

### 2. The Ruler: Standard Deviation of DDLT ($\sigma_{DDLT}$)

This is the physical length of one standard deviation. It is the Pythagorean hypotenuse of your independent customer risk and supplier risk (Eve's Law).

- **Formula:** $\sigma_{DDLT} = \sqrt{\mu_L \sigma_D^2 + \mu_D^2 \sigma_L^2}$
- **In English:** The mathematically proven size of your combined risk.

### 3. The Armor: Safety Stock ($SS$)

You take the size of your risk ($\sigma_{DDLT}$) and multiply it by how many standard deviations the business wants to cover ($Z$).

- **Formula:** $SS = Z \times \sigma_{DDLT}$
- **Expanded:** $SS = Z \times \sqrt{\mu_L \sigma_D^2 + \mu_D^2 \sigma_L^2}$
- **In English:** The exact number of extra units you must stack on top of your baseline inventory to absorb the targeted percentage of chaos.

### 4. The Trigger: Reorder Point ($ROP$)

The final deterministic integer that your Python engine calculates to trigger a new purchase order. It is simply the anchor plus the armor.

- **Formula:** $ROP = E[DDLT] + SS$
- **In English:** The absolute minimum number of units you can hold in your warehouse before you must call the supplier to survive the lead time with a $Z$% success rate.

## Part 8: The Infinity Clash (Optimizer Context)

The derivation above computes a **finite** safety stock target $SS_t$ outside the optimizer by chopping the infinite tail of forecasted demand at a chosen service level. A separate problem arises when $C_{shortage} \to \infty$ is applied **inside** a Mixed-Integer Linear Program (MILP) against statistical forecasts.

### 1. The Core Problem

In medical devices, failing to deliver a surgical kit carries a near-infinite business penalty. If an OR architect applies a near-infinite $C_{shortage}$ against general forecasted demand within a MILP, the solver falls into an **Unbounded Optimization Trap**: because forecasted demand follows a normal distribution with an infinite statistical tail, the solver demands infinite inventory to guarantee zero stockouts.

To prevent mathematically bankrupting the company, risk must be decoupled into **Statistical Buffers** (computed outside the optimizer) and **Stratified Linear Penalties** (applied inside the optimizer).

### 2. Mathematical Components (Soft vs. Hard Constraints)

| Symbol | Role |
|--------|------|
| **$SS_t$** | Statistical target calculated outside the optimizer (e.g., 99.0% service level → finite unit target). |
| **$V_t$** | Slack variable: units by which inventory $I_t$ falls short of $SS_t$. Constraint: $I_t + V_t \ge SS_t$. |
| **$C_{violation}$** | Moderate financial penalty on $V_t$ when the optimizer dips below the buffer. |
| **$C_{shortage}$** | Near-infinite penalty applied **only** when the optimizer fails to fulfill a physical, legally binding customer order. |

### 3. Application by Demand State

The mechanism depends on whether demand is **Forecasted** (Peace Time) or **Firmed** (War Time). See [Two_Dials_Framework.md](../frameworks/Two_Dials_Framework.md) for the operational closed-loop workflow.

**Situation A: Forecasted Demand (Macro / S&OP)**

- Environment: Slushy/Liquid zones; no immediate firm purchase orders.
- Mechanism: Remove near-infinite $C_{shortage}$ from the matrix. Treat $SS_t$ as a rigid requirement. Optimize factory shifts and working capital to build the buffer using peacetime capacity.

**Situation B: Firmed Demand & Operational Chaos (Micro / Triage)**

- Environment: Frozen zone; machine breakdown or firm hospital order due tomorrow.
- Mechanism: Inject both $V_t$ and near-infinite $C_{shortage}$ on the firm order simultaneously.
- Triage logic: The solver compares (1) protecting $SS_t$ and missing the firm order vs (2) activating $V_t$ (draining buffer), fulfilling the order, and incurring $C_{violation} \cdot V_t$. Path 2 wins — mirroring elite supply-planner triage.

**Layer 4 invariants:** When a MILP uses slack on safety stock, assert $V_t \ge 0$ and $I_t + V_t \ge SS_t$ for all $t$; verify $C_{shortage}$ is attached only to firm-order shortage variables, not forecast rows.

## Related Notes

- [projects/mrp/README.md](../../../../Notes/projects/mrp/README.md) — MRP project notes index.
- [projects/mrp/supply-planning/frameworks/Two_Dials_Framework.md](../frameworks/Two_Dials_Framework.md) — peace/war demand-state application of triage penalties.
- [meta/OR_AI_ASI.md](../../../../Notes/meta/OR_AI_ASI.md) — OR framework and supply-planning pillar examples.
- [meta/Layer4_TypeB_Auditing.md](../../../../Notes/meta/Layer4_TypeB_Auditing.md) — invariant auditing for deterministic engines.
