# FlashCase Success Metrics

> Comprehensive metrics framework for measuring FlashCase's success

## North Star Metric

**Cards Successfully Retained (30+ days)**
- Measures actual learning effectiveness, not just usage
- Target: 1M+ cards retained monthly by our users
- Why: Retention is the ultimate goal; this metric captures real learning outcomes

---

## Metric Categories

### 1. Engagement Metrics 📊

Track how users interact with the product on a daily basis.

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| Daily Active Users (DAU/MAU) | 40%+ | DAU divided by MAU | P0 |
| Cards Reviewed Per Session | 50+ | Average cards per session | P0 |
| Study Streak | 60%+ maintain 7+ days | % users with 7-day streaks | P1 |
| Time Per Session | 20-30 minutes | Average session duration | P1 |
| Sessions Per Week | 5+ | Average for active users | P1 |
| Feature Adoption - Community Decks | 70%+ | % users who try community decks | P2 |
| Feature Adoption - AI Generation | 40%+ | % users who use AI generation | P2 |

**Why These Matter:**
- High engagement indicates product value and habit formation
- Study streaks correlate with learning effectiveness
- Feature adoption shows which capabilities provide value

---

### 2. Retention Metrics 🔄

Measure how well we keep users coming back over time.

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| D1 Retention | 60%+ | % users return next day | P0 |
| D7 Retention | 40%+ | % users return after week | P0 |
| D30 Retention | 25%+ | % monthly active users | P0 |
| Churn Rate | <10% monthly | % users who stop using | P1 |
| Semester Retention | 70%+ | % active throughout semester | P1 |
| Resurrection Rate | 20%+ | % churned users who return | P2 |

**Why These Matter:**
- D1 retention is critical for habit formation
- Semester retention indicates sustained value
- Low churn = product-market fit

**Cohort Analysis:**
- Track retention by acquisition channel
- Compare retention by user segment (1L, 2L, 3L, bar candidates)
- Identify features that improve retention

---

### 3. Learning Effectiveness Metrics 🧠

Measure actual learning outcomes and efficiency gains.

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| Card Retention Rate | 80%+ | % cards remembered at intervals | P0 |
| Mastery Rate | 60%+ | % cards reach "mastered" status | P0 |
| Study Efficiency | 30%+ improvement | Time saved vs. traditional methods | P1 |
| Exam Performance | 70%+ report improvement | Self-reported grade improvement | P2 |
| Bar Pass Rate | Track | % of users who pass bar | P2 |

**Why These Matter:**
- Core value proposition is improved learning
- These metrics validate our spaced repetition algorithm
- Self-reported improvements drive word-of-mouth growth

**Measurement Methods:**
- Algorithm tracking of card performance
- User surveys before/after exams
- Follow-up surveys with bar exam takers
- A/B testing of algorithm variations

---

### 4. Community & Growth Metrics 👥

Track community health and viral growth.

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| Deck Sharing Rate | 20%+ | % users who create public decks | P1 |
| Community Deck Usage | 80%+ | % users who access shared decks | P1 |
| Referral Rate | 30%+ | % users who invite classmates | P1 |
| Net Promoter Score (NPS) | 50+ | Promoter % - Detractor % | P0 |
| Viral Coefficient | 0.3+ | New users per existing user | P2 |
| Content Quality Score | 4.0+ | Average rating of top decks | P1 |

**Why These Matter:**
- Community content reduces our content creation burden
- Organic growth through referrals has best economics
- High NPS indicates strong product-market fit

**NPS Calculation:**
- Survey: "How likely are you to recommend FlashCase to a classmate?" (0-10)
- Promoters (9-10), Passives (7-8), Detractors (0-6)
- NPS = % Promoters - % Detractors

---

### 5. Cost & Business Metrics 💰

Track unit economics and business sustainability.

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| Customer Acquisition Cost (CAC) | <$15 | Total marketing spend / new users | P0 |
| Lifetime Value (LTV) | >$60 | Average revenue per user lifetime | P0 |
| LTV:CAC Ratio | 4:1+ | LTV divided by CAC | P0 |
| Free to Paid Conversion | 10%+ | % free users who upgrade | P1 |
| Monthly Recurring Revenue (MRR) | Track growth | Sum of all monthly subscriptions | P0 |
| Hosting Cost Per User | <$0.50/month | Infrastructure costs / MAU | P1 |
| AI Cost Per User | <$0.10/month | AI processing costs / MAU | P1 |
| Gross Margin | >70% | (Revenue - COGS) / Revenue | P1 |

**Why These Matter:**
- Unit economics determine business viability
- LTV:CAC ratio indicates scalability
- Cost per user affects pricing strategy

**Cost Breakdown:**
- Infrastructure: Hosting, database, CDN, storage
- AI: API costs for generation features
- Support: Customer service and community moderation
- Development: Ongoing feature development

---

### 6. AI Feature Metrics 🤖

Track AI-powered content generation effectiveness.

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| AI Generation Usage | 40%+ monthly | % active users who use AI | P1 |
| AI Content Quality | 80%+ cards kept | % AI cards retained/used | P0 |
| Generation Success Rate | 95%+ | % successful extractions | P1 |
| Generation Cost | <$0.10/user/month | AI API costs per user | P1 |
| Processing Time | <30 seconds | Average generation time | P2 |
| Cards Per Generation | 5-8 average | Cards generated per request | P2 |

**Why These Matter:**
- AI is key differentiator vs. competitors
- Quality must be high to maintain trust
- Costs must be sustainable at scale

**Quality Measurement:**
- User feedback on generated cards
- Edit rate (how often users modify cards)
- Deletion rate (cards generated but deleted)
- Comparison with manually created cards

---

### 7. Acquisition Metrics 📈

Track how users discover and sign up for FlashCase.

| Metric | Target | Measurement | Channel |
|--------|--------|-------------|---------|
| Website Visitors | Track | Monthly unique visitors | All |
| Sign-up Conversion Rate | 25%+ | % visitors who create account | All |
| Time to Value | <5 minutes | Time from signup to first review | Product |
| Organic Traffic | 50%+ of total | Visitors from search/direct | SEO |
| Referral Traffic | 30%+ of total | Visitors from existing users | Word-of-mouth |
| Paid Traffic | <20% of total | Visitors from ads | Marketing |

**Acquisition Channels:**
- **Organic**: SEO, direct traffic, content marketing
- **Referral**: Word-of-mouth, in-app referrals
- **Paid**: Social media ads, search ads
- **Partnerships**: Law school partnerships, bar prep affiliates
- **Content**: Blog posts, study guides, YouTube tutorials

---

## Metric Dashboard Structure

### Executive Dashboard (Weekly Review)
- North Star Metric: Cards Successfully Retained
- MAU and DAU
- MRR and growth rate
- NPS score
- Key issues or anomalies

### Product Team Dashboard (Daily Review)
- DAU and session metrics
- Feature adoption rates
- Retention cohorts
- Bug and issue tracking

### Growth Team Dashboard (Weekly Review)
- Acquisition by channel
- Conversion funnel metrics
- Referral and viral metrics
- CAC by channel

### Engineering Dashboard (Real-time)
- System uptime and performance
- API response times
- Error rates
- AI processing costs

---

## Measurement Tools & Implementation

### Analytics Platform
- **Tool**: Mixpanel, Amplitude, or similar
- **Events to Track**:
  - User signup and onboarding completion
  - Card creation (manual, AI, import)
  - Card review and performance
  - Deck creation and sharing
  - Feature usage (AI generation, community browse)
  - Session start/end

### A/B Testing Platform
- **Tool**: Optimizely, LaunchDarkly
- **Tests to Run**:
  - Onboarding flow variations
  - Spaced repetition algorithm parameters
  - Pricing and packaging
  - UI/UX improvements
  - AI prompt variations

### User Feedback
- **In-App Surveys**: NPS, feature satisfaction
- **User Interviews**: Monthly with 5-10 users
- **Support Tickets**: Track common issues
- **Usage Data**: Behavioral analytics

---

## Targets by Phase

### Phase 1: Alpha (Months 1-3)
- **Users**: 20-50 beta testers
- **Focus**: Validate core value proposition
- **Key Metrics**:
  - D1 Retention: >50%
  - Cards Reviewed/Day: 30+
  - NPS: 40+

### Phase 2: Beta (Months 4-6)
- **Users**: 200-500
- **Focus**: Achieve product-market fit
- **Key Metrics**:
  - D1 Retention: >55%
  - D7 Retention: >35%
  - Cards Reviewed/Day: 40+
  - NPS: 45+

### Phase 3: Growth (Months 7-12)
- **Users**: 2,000-5,000
- **Focus**: Scale and monetization
- **Key Metrics**:
  - D1 Retention: >60%
  - D30 Retention: >25%
  - Free to Paid: >8%
  - NPS: 50+
  - LTV:CAC: >3:1

### Phase 4: Scale (Year 2+)
- **Users**: 20,000-50,000
- **Focus**: Market leadership
- **Key Metrics**:
  - All targets from metrics table
  - Market share: 20%+ in target schools
  - Brand awareness: 60%+ recognition

---

## Metric Review Cadence

### Daily
- **Owner**: Product Manager
- **Metrics**: DAU, MAU, system health
- **Action**: Identify anomalies, critical issues

### Weekly
- **Owner**: Product & Growth Teams
- **Metrics**: All engagement and retention metrics
- **Action**: Feature adjustments, growth experiments

### Monthly
- **Owner**: Leadership Team
- **Metrics**: All metrics, focus on trends
- **Action**: Strategy adjustments, resource allocation

### Quarterly
- **Owner**: Exec Team + Board
- **Metrics**: Business metrics, strategic goals
- **Action**: Major pivots, roadmap updates

---

## Red Flags & Alerts

Set up automated alerts for concerning trends:

### Critical Alerts (Immediate Action)
- DAU drops >15% week-over-week
- System uptime <99.5%
- AI costs spike >50%
- D1 retention drops below 50%

### Warning Alerts (Review Within 24h)
- NPS drops below 40
- Churn rate increases >3% month-over-month
- CAC exceeds $20
- Card retention rate below 75%

### Watch Alerts (Review Weekly)
- Feature adoption below targets
- Referral rate declining
- Support tickets increasing

---

## Benchmarking

### Industry Benchmarks (EdTech)
- D1 Retention: 40-60% (we target high end)
- D30 Retention: 15-25% (we target high end)
- NPS: 30-50 (we target 50+)
- Free to Paid: 2-5% (we target 10%+)

### Competitive Benchmarks
- **Anki**: High retention but complex, steep learning curve
- **Quizlet**: Broad adoption, lower retention for serious study
- **Bar Prep**: High engagement during study period, then churn

### Our Advantage
- Law-specific features drive higher engagement
- AI features provide unique value
- Community creates network effects
- Better UX than Anki, more serious than Quizlet

---

## Metric Definitions & Formulas

### Active User Definitions
- **Daily Active User (DAU)**: Reviewed at least 1 card today
- **Monthly Active User (MAU)**: Reviewed at least 1 card in last 30 days
- **Engaged User**: 5+ sessions per week, 100+ cards per month

### Retention Formulas
```
D1 Retention = (Users active on Day 1) / (Users who signed up on Day 0)
D7 Retention = (Users active on Day 7) / (Users who signed up on Day 0)
Churn Rate = (Users who left) / (Users at start of period)
```

### Business Formulas
```
CAC = Total Marketing & Sales Spend / New Users Acquired
LTV = ARPU × Average Customer Lifetime (months)
LTV:CAC = LTV / CAC
MRR = Sum of all monthly recurring revenue
```

### Learning Effectiveness
```
Card Retention = (Cards recalled correctly) / (Total cards reviewed)
Mastery Rate = (Cards at mastery level) / (Total cards reviewed 3+ times)
```

---

## Data Privacy & Ethics

### User Data Principles
- Collect only necessary data for product improvement
- Anonymize data for analysis when possible
- Never sell user data to third parties
- Allow users to export and delete their data
- Transparent about what we track and why

### Ethical Considerations
- Don't gamify in ways that encourage unhealthy behavior
- Respect study-life balance (don't push to extremes)
- Content moderation to prevent cheating/plagiarism
- Protect student privacy (especially grades, performance)

---

## Success Criteria Summary

FlashCase will be considered successful when we achieve:

✅ **Product-Market Fit**
- NPS of 50+
- 60%+ D1 retention
- 25%+ D30 retention
- Organic growth through referrals

✅ **Learning Effectiveness**
- 80%+ card retention rate
- 70%+ users report improved outcomes
- 30%+ study time savings

✅ **Business Viability**
- LTV:CAC ratio of 4:1+
- 10%+ free to paid conversion
- Positive unit economics
- Sustainable growth rate

✅ **Market Position**
- 5,000+ active users by end of year 1
- 20%+ market share in target schools by year 2
- Category leader in legal education tools

---

**Last Updated**: October 2025  
**Owner**: Product & Analytics Teams  
**Review Frequency**: Updated monthly  

For questions about metrics or to request new dashboards, contact the analytics team.
