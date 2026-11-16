# Amazon review analysis: plant-oil mouse repellents (competitor products)

Source: Apify dataset `40u69Do2RtPEbKNct`, 320 Amazon reviews, read in full on 2026-11-16.

**These are reviews of competitor products. None of them is a review of our product.** Nothing here is evidence about how our pouches perform. It is evidence about what buyers of similar products expect, say, and complain about.

---

## 1. Method and sample

**Rows read:** 320 of 320 (8 pages of 40). Every row was read and tagged by hand; nothing was sampled. All 320 rows are marked `verified: true`. Most reviews are dated 2025-2026; a handful are from 2020-2024.

**Tagging:** each review got one or more theme tags, plus use location, other methods mentioned, and emotion. A review can carry several themes, so theme shares add up to more than 100%. Counts come from manual reading, so treat every count as accurate to within a few reviews, not as an exact measurement. Short reviews ("Didn't work") carry one tag and no location.

**Per product**

| ASIN | Product | Critical (1-3 star) | Positive (4-5 star) | Total |
|---|---|---|---|---|
| B07JMDYDVJ | Grandpa Gus's pouches, peppermint + cinnamon, 10 pack | 40 | 30 | 70 |
| B0DK9Y2LTR | Mighty Mint pouches with glue dots, 12 count | 30 | 20 | 50 |
| B0GMYLJSKV | Rodent repellent pouches 12-pack (reviewers call it "Sofyre") | 40 | 0 | 40 |
| B0FVLPXRNY | "Pest Rodent Repellent" 24 pack peppermint balls | 30 | 0 | 30 |
| B0DDNSN224 | Pouches made in USA, 12 pouches | 30 | 0 | 30 |
| B0F62YTG6V | Mouse rodent repellent 24 pack peppermint | 30 | 0 | 30 |
| B07HYP6D5C | Mighty Mint peppermint oil spray, 16 oz | 30 | 0 | 30 |
| B07N6JZ2J4 | Battery ultrasonic under-hood repeller | 20 | 0 | 20 |
| B0H7HY5CBT | Rodent Away pouches, 12 pack | 0 | 20 | 20 |
| **Total** | | **250** | **70** | **320** |

Star split: critical = 145 three-star, 77 two-star, 28 one-star. Positive = 43 five-star, 27 four-star.

**Four limits on this sample that change how to read it**

1. **The critical set leans mild.** 58% of the critical reviews are three-star. About 12 of the 250 are in fact happy ("They work!") and another 33 are "can't tell yet". The angry one-star voice is under-represented outside B0DDNSN224.
2. **Positive reviews exist for only three products.** There is no positive sample for six of the nine ASINs, so praise themes describe Grandpa Gus's, Mighty Mint and Rodent Away buyers only.
3. **The 20 Rodent Away (B0H7HY5CBT) reviews should not be trusted as customer voice.** Eight of them contain the literal sentence "In this fictional scenario, I'm a ..." and several repeat whole paragraphs word for word. The other twelve read like the same template (tidy-routine stories, search keywords dropped mid-sentence such as "mouse deterrents that work", almost no stated result). I have counted them separately throughout and kept them out of the phrase list in section 6. Do not lift testimonials or language from them.
4. **Two products are not pouches.** The spray (30) and the ultrasonic device (20) are included because the same buyers move between them. Where it matters I give a pouch-only figure (200 critical pouch reviews).

**Emotion in the critical reviews (approximate):** flat disappointment about 108, neutral/matter-of-fact 31, anger 26, uncertainty 20, annoyance 17 (mostly smell), resignation 9 ("Just like everything else"), frustration 7, scepticism 7. Fear and desperation are rare in count (about 4) but appear in the most-upvoted reviews: disease from deer mice, wiring fires, repair bills.

---

## 2. Complaint themes, ranked (base: 250 critical reviews)

| # | Theme | Count | Share of critical |
|---|---|---|---|
| 1 | Did nothing: still have mice, mice walked over it or sat next to it | 121 | 48% |
| 2 | Bought it for an animal it does not repel (groundhogs, squirrels, chipmunks, moles, raccoons, spiders, ants) | 36 | 14% |
| 3 | Cannot tell whether it works / too early to say | 33 | 13% |
| 4 | Rodents ate, chewed, dragged off, nested on or threw out the pouch | 27 | 11% |
| 5 | Scent faded in days or weeks | 26 | 10% |
| 6 | Price for what you get / waste of money | 25 | 10% |
| 7 | Worked at first, then they came back | 17 | 7% |
| 8 | Scent too strong: headaches, could not sleep, left the house | 16 | 6% |
| 9 | Smells wrong: mothballs, not peppermint | 16 | 6% |
| 10 | Device or packaging failed (sprayer broke 6, ultrasonic died 6, fiddly use 4) | 16 | 6% |
| 11 | Have to replace too often | 9 | 4% |
| 12 | Scent too weak, little smell on arrival | 8 | 3% |
| 13 | "Helps, but is not a solution" | 7 | 3% |
| 14 | Too few for the space / unclear how many to use | 7 | 3% |
| 15 | Seemed to attract them | 5 | 2% |
| 16 | Vehicle wiring or nest damage happened anyway | 5 | 2% |
| 17 | Pet, bird or child safety worries | 4 | 2% |
| 18 | Trust: knock-off worries, ingredient doubts, "not as advertised" smell, billing | 10 | 4% |
| 19 | Refund friction | 3 | 1% |
| 20 | Mess (powder, oil on hands, torn bags) | 3 | 1% |

Useful combinations: themes 1 or 4 together = 132 reviews (53%). Any longevity complaint (themes 5, 7 or 11) = 43 reviews (17%). Any smell complaint (themes 8 or 9) = 26 reviews (10%). Pouch-only base of 200: did nothing 101 (51%), ate/chewed 27 (14%), faded 23 (12%), price 20 (10%).

Two themes I expected and did not find as stated: nobody says the pouches arrived **dried out** (the nearest is weak scent and one person wondering "if it expired or something"), and nobody in the critical set openly accuses the listing of **fake reviews**. What appears instead is the reverse: buyers say they bought because of the reviews and then felt let down (see 2.18). Oil stains on surfaces do not appear either; the nearest is a smell that "stains your clothes" and one leaked spray bottle.

### 2.1 Did nothing: still have mice, mice ignored it (121, 48%)

The single dominant complaint, and the one with the most helpful votes (about 300 votes across these reviews). The image buyers use again and again is a mouse right beside the pouch.

- "Mouse sat right next to it and nothing happened" (B0DK9Y2LTR, 3 stars, 1 helpful)
- "This product DID NOT perform as expected. I used all 12 pouches in an 1100 square foot apartment. That was three weeks ago. The return window is nearly up, and I am still seeing mice." (B0DK9Y2LTR, 3 stars, 8 helpful)
- "after only 5 days of use, another mouse was caught in the trap, which was literally an inch or two away from one of these Sofyre pouches" (B0GMYLJSKV, 2 stars, 34 helpful)
- "I bought this with hopes it would work and well it doesn’t I put around the area where mice are coming in and well they just walk over it" (B0GMYLJSKV, 2 stars, 9 helpful)
- "They smell really nice and have a very strong smell, but the mice completely ignored them and were back the same evening I put them out. But our garage smells good though." (B0DDNSN224, 1 star, 3 helpful)
- "Did not work. Had a mouse hole in my pantry. Stuffed one of these in the whole and put two more leaning on the sme shelf. They still broke in and ate my hamburger buns on the same shelf." (B0DDNSN224, 1 star, 1 helpful)
- "Literally opened a drawer that had 2 of these in it to see a mouse sitting there next to one of them so they clearly do not work as advertised." (B0F62YTG6V, 2 stars, 0 helpful)
- "I put three of them under the hood of my car in various, safe spots, and it is not keeping the rodents out." (B07JMDYDVJ, 3 stars, 13 helpful)

### 2.2 Bought it for an animal it does not repel (36, 14%)

Concentrated in B0GMYLJSKV (11) and B0FVLPXRNY (8), whose listings evidently reach people with groundhogs, moles and chipmunks. These buyers blame the product, not themselves.

- "Inserted into hole groundhog removes it. Tied it to a flat rock groundhog removes rock. Stabled it to a 2x4 and inserted 4 feet into the hole. Groundhog removed packet and placed it outside the hole." (B0GMYLJSKV, 2 stars, 21 helpful)
- "If it not meant for groundhogs may be it would be a good idea to make it clear on package." (B0GMYLJSKV, 2 stars, 21 helpful, same review)
- "Did not work at all for groundhogs. They just kicked them right out of the hole LOL" (B0GMYLJSKV, 2 stars, 0 helpful)
- "Other like brands say the mouse family which does include squirrels, this product Does not work on squirrels." (B07JMDYDVJ, 3 stars, 1 helpful)
- "Doesn’t specifically say squirrels but they are rodents and this DOES NOT work on them." (B07HYP6D5C, 2 stars, 0 helpful)
- "Was hoping these would keep chipmunks out of my planter pots, but no effect at all." (B0FVLPXRNY, 3 stars, 1 helpful)
- "It may have kept the small mice out but it attracted raccoons which destroyed the interior and they even ate the packets." (B0DK9Y2LTR, 2 stars, 0 helpful)

### 2.3 Cannot tell whether it works (33, 13%)

A repellent's success is an absence, and buyers have no way to see it. Many post a three-star "not sure".

- "Who knows if they are working?" (B0GMYLJSKV, 3 stars, 0 helpful)
- "not really sure how to tell if these are really doing anything" (B0GMYLJSKV, 3 stars, 1 helpful)
- "No mice came running out. Hard to tell if it will work." (B0GMYLJSKV, 3 stars, 5 helpful)
- "Using them in my feed room. Saw turds 4 days later. Put another one out. Haven't seen any more in 3 days." (B0DK9Y2LTR, 3 stars, 0 helpful)
- "I don't know if the sachets are making a difference or not" (B07JMDYDVJ, 3 stars, 11 helpful)
- "I probably would not buy again, but I can't say if they work, or not." (B07N6JZ2J4, 3 stars, 1 helpful)
- From a four-star review, the same doubt: "Have no idea if it's working as far as keeping mice away. How does one know? I marked calendar for 30 days. Does it have to be repeated ?? Does anyone know??" (B07JMDYDVJ, 4 stars, 1 helpful)

### 2.4 Rodents ate, chewed, dragged off or nested on the pouch (27, 11%)

20 of these are mice or rats; 7 are groundhogs, moles or raccoons pushing packets out of burrows. This is the most damaging single image in the data: it turns "it did not work" into "it is a joke". B0DDNSN224 (9) and B0GMYLJSKV (10) carry most of it.

- "we watched them walk right up to the product and drag it away. has not deterred their presence or habits in the least" (B07JMDYDVJ, 3 stars, 30 helpful)
- "I opened the shed twenty-four hours later to find not only had she chewed both pouches, but she built a nest on top of one of them." (B07JMDYDVJ, 2 stars, 6 helpful)
- "The mice started eating this bait" (B07JMDYDVJ, 3 stars, 8 helpful)
- "i have placed these pouches everywhere, not only do they not work, I saw the mouse dragging it." (B0DDNSN224, 1 star, 11 helpful)
- "Not worth the money. Mice were eating the packets. Actually seen more mice with the packets being placed around." (B0DDNSN224, 1 star, 1 helpful)
- "My husband pulled down one of the lights in trailor where we had placed a packet and found that a mouse had started eating the packet." (B0GMYLJSKV, 2 stars, 1 helpful)
- "The rat took this and ran away with it. I'm not even exaggerating." (B0FVLPXRNY, 3 stars, 1 helpful)
- "These didnt work for us. The mice literally make their home right next to the packs." (B0DDNSN224, 1 star, 2 helpful)

### 2.5 Scent faded in days or weeks (26, 10%; 31 with "replace too often")

Stated lifetimes in the complaints: half an hour (spray), 24 hours, 2 days, 3 days, "a few days", under a week, a week, 10 days, a couple of weeks, a month. Nobody in the critical set reports a pouch lasting anywhere near 90 days.

- "They do help but do not get the mice out for good. They only last about 10 days." (B0DK9Y2LTR, 3 stars, 2 helpful)
- "They smell very strong minty odor, but it fades away within a week." (B0DK9Y2LTR, 3 stars, 1 helpful)
- "Scent leaves quickly. Within a week I could hardly smell the pouches." (B0GMYLJSKV, 3 stars, 5 helpful)
- "I mean bugs and rats do stay away for a little bit but the scent wares off quickly and in about a month, you'll be needing another one." (B07JMDYDVJ, 3 stars, 13 helpful)
- "The scent doesn’t stay long at all . Would be much better if it did. Don’t even stay a full week . Too much money for that short time ." (B07JMDYDVJ, 2 stars, 0 helpful)
- "Plus the scent only lasted about 24 hours" (B07JMDYDVJ, 2 stars, 0 helpful)
- "The scent is pleasant but it only lasted for about two days" (B0FVLPXRNY, 2 stars, 0 helpful)
- "these packs do not last very long so you would need to buy a very high volume to get you through the winter" (B07JMDYDVJ, 3 stars, 0 helpful)

Note that buyers judge the product's life by whether **they** can still smell it. One says so: "sent didnt seem to last as long as I expected maybe I just got used to it" (B07JMDYDVJ, 3 stars, 1 helpful).

### 2.6 Price for what you get (25, 10%)

Rarely a standalone complaint. It is the multiplier on "did nothing" or "faded fast".

- "Cost is high for mouse repellent." (B0GMYLJSKV, 2 stars, 21 helpful)
- "I'm doubtful that they deter much, and the scent doesn't last long for as much as they cost." (B07JMDYDVJ, 3 stars, 0 helpful)
- "Definitely looking for a better product. I do not recommend this product. Honestly I wasted my money." (B07JMDYDVJ, 2 stars, 0 helpful)
- "Horrible product not worth the money or the time." (B0DDNSN224, 1 star, 11 helpful)
- "Seems to work great but the exact same product same size, $25 at home depot." (B07JMDYDVJ, 3 stars, 0 helpful)
- "I am convinced these are basically an overpriced battery operated little black box that lights up periodically." (B07N6JZ2J4, 3 stars, 6 helpful)
- From a four-star review: "In my opinion product becomes expensive having to buy the product frequently." (B07JMDYDVJ, 4 stars, 15 helpful)

### 2.7 Worked at first, then they came back (17, 7%)

The return usually tracks the scent fading. Typical window: 2 days to a month, most often about a week.

- "Just like everything else. They worked great for the first week. Then the mice just walked on them." (B0DK9Y2LTR, 3 stars, 0 helpful)
- "Worked great for about 7 days but after that week. They were back leaving droppings in their favorite spots." (B07JMDYDVJ, 2 stars, 0 helpful)
- "Did not see any sign of mice for about a month. Then they came back. I did not think a month was my idea of rodent control." (B0F62YTG6V, 3 stars, 16 helpful)
- "This only worked for like 5 days after that it did nothing. Even with new packs down the mice kept coming." (B0DDNSN224, 1 star, 2 helpful)
- "For a couple weeks they seemed to work, but then there was clear evidence of the return of the vermin." (B0FVLPXRNY, 3 stars, 1 helpful)
- "Very fragrant it is a pouch, but the fragrance dies, and they come back" (B0DK9Y2LTR, 3 stars, 0 helpful)
- "At first we thought mice were gone. Didn't hear them in the walls anymore until within 1 month we are hearing them again." (B0GMYLJSKV, 2 stars, 1 helpful)

### 2.8 Scent too strong (16, 6%)

Ten of the 16 are B0F62YTG6V. On the peppermint products this complaint is rare and usually tied to using too many indoors.

- "I also got a very heavy duty migraine headache because he put too many under the house." (B07JMDYDVJ, 3 stars, 5 helpful)
- "the smell is so overpowering I ran away from my house!" (B0F62YTG6V, 3 stars, 1 helpful)
- "We put the kids to bed, and after trying to fall asleep for about a half hour, I couldn’t take the smell anymore. I got up and rounded them up and set them in a bag outside in the middle of the night." (B0F62YTG6V, 1 star, 3 helpful)
- "The smell made we want to leave but unfortunately not the rats." (B0DDNSN224, 1 star, 7 helpful)
- "After putting a few in the house, I got a stuffy nose and throat pain." (B0FVLPXRNY, 3 stars, 0 helpful)
- "It about knocks me out when I walk in the house and reminds me of the mouse issue." (B0F62YTG6V, 1 star, 3 helpful)

### 2.9 Smells wrong: mothballs, not peppermint (16, 6%)

15 of 16 are one product, B0F62YTG6V. Buyers read it as a broken promise about ingredients, not just an unpleasant smell.

- "These are marketed as smelling of peppermint and being a good repellent because they contain peppermint. These are mothballs. They reek of mothball." (B0F62YTG6V, 3 stars, 12 helpful)
- "it reeks of the scent of moth balls.So now all of the clothes in my closet stink." (B0F62YTG6V, 3 stars, 0 helpful)
- "I truly question the claim of natural ingredients ~ lemongrass & peppermint oil should not in anyway resemble the smell of chemically toxic mothballs." (B0F62YTG6V, 2 stars, 1 helpful)
- "It's strong. The type of strong that stains your clothes, your furniture, and everything else." (B0F62YTG6V, 3 stars, 1 helpful)
- "the smell is nothing like peppermint. It smells like deer repellent which is not pleasant." (B0FVLPXRNY, 3 stars, 1 helpful)
- "It stinks like moth balls. It does NOT smell like peppermint at all!!" (B0F62YTG6V, 2 stars, 0 helpful)

### 2.10 Scent too weak (8, 3%)

- "each sachet by itself has such a mild scent that we had to put it up against our noses to be able to smell it" (B07JMDYDVJ, 3 stars, 11 helpful)
- "this kind of made me wonder if it expired or something" (B07JMDYDVJ, 3 stars, 11 helpful, same review)
- "Not as strong of the peppermint scent they said it would be" (B07JMDYDVJ, 3 stars, 0 helpful)
- "The smell is not strong, I placed one bag on the counter and the next morning there was mouse poop next to it." (B0DDNSN224, 1 star, 1 helpful)
- "Scent is not as strong as hoped. Placed in my car, can only smell the peppermint if the air conditioner is on." (B0FVLPXRNY, 3 stars, 0 helpful)
- "I did not get the strong minty fragrance from the first few packets opened as some have reported on their review." (B0FVLPXRNY, 2 stars, 1 helpful)

### 2.11 Replace too often, and how many do I need (9 + 7)

- "Not happy that I have to replace these monthly didn't read that in the details" (B0DK9Y2LTR, 2 stars, 0 helpful)
- "I don’t think I want to buy a new box every month or two. Was hoping they’d work for a lot longer." (B0FVLPXRNY, 3 stars, 1 helpful)
- "I would have to buy over and over again every month." (B0F62YTG6V, 3 stars, 16 helpful)
- "it seems that I would have to have these pouches laid out everywhere at a one foot spacing in every room and space to see if any mice still show up" (B0GMYLJSKV, 3 stars, 1 helpful)
- "I put all 12 bags out in a shop building that is 30'x40' and it did nothing to help. This is way more than the suggested amount needed to cover such sq footage according to the packaging and still ZERO EFFECT." (B0DDNSN224, 1 star, 1 helpful)
- "they work but need lots" (B0FVLPXRNY, 3 stars, 0 helpful)
- "Read the directions carefully you only need one for 50 square feet." (B07JMDYDVJ, 3 stars, 5 helpful)

### 2.12 Vehicle and RV damage happened anyway (5 explicit; 21 critical reviews concern vehicles)

Mostly from the ultrasonic device, but the stakes are the same for pouch buyers.

- "squirrels built a nest to give birth to a baby, and ate my Toyota Tacoma wiring harness even though my Ultrasonic was in and working properly" (B07N6JZ2J4, 3 stars, 1 helpful)
- "guess what? Yep, a newly started mouse nest front and center on top of my engine!" (B07N6JZ2J4, 3 stars, 6 helpful)
- "another Nest was just starting. Right next to the unit 6 in away from the unit with flashing lights" (B07N6JZ2J4, 2 stars, 0 helpful)
- "I had mice in my car and I put these in the trunk and on the floors in the car. The mice urinated on them." (B07JMDYDVJ, 2 stars, 0 helpful)
- "After cleaning under the hood I used 3 pouches. Checked a few days later and it was evident the rodents came back." (B07JMDYDVJ, 3 stars, 13 helpful)

### 2.13 Seemed to attract them (5)

- "Does not work! If anything, I felt like it attracted them." (B0DK9Y2LTR, 1 star, 1 helpful)
- "Are they more attracted to the mints over actual food??" (B0FVLPXRNY, 2 stars, 0 helpful)
- "Didn’t seem to keep any of the animals away- in fact they seemed interested in it." (B07HYP6D5C, 3 stars, 0 helpful)
- "We’ve lived in this older house for five years, and I’ve never seen so much activity until after using these." (B0DK9Y2LTR, 1 star, 1 helpful)

### 2.14 Pets, birds, children (4)

- "Directions on line say pet and children safe but the box says keep away from pets and children." (B0FVLPXRNY, 3 stars, 3 helpful)
- "Been advised by Vet & others to not use inside at all & only lightly if used outside so it doesn't seep into the indoors cuz the strong oils could harm pets' kidneys, liver, lungs...." (B07JMDYDVJ, 2 stars, 0 helpful)
- "Not bird safe." (B07JMDYDVJ, 3 stars, 5 helpful)
- "I don’t feel like they are as safe a nontoxic as the say. They have highly concentrated essential oils, which I’ve read can be harmful if kids get them." (B0F62YTG6V, 1 star, 3 helpful)

Safety is far more often a reason to buy than a complaint: see section 4, "poison".

### 2.15 Mess (3 critical, plus 1 in a positive review)

- "They chewed and destroyed 3 packs so the powder was fun to pick up" (B07JMDYDVJ, 2 stars, 4 helpful)
- "Mice chew through packs and make a mess!!" (B07JMDYDVJ, 2 stars, 0 helpful)
- "put some gloves on that you don’t care about because it stays on your hands when you are placing it into the small bag. I washed my hands 5 times before the smell was gone." (B0F62YTG6V, 3 stars, 2 helpful)
- "Some bags were torn open leaked all over the place." (B07JMDYDVJ, 4 stars, 0 helpful)

### 2.16 Device and packaging failures (16; spray and ultrasonic only)

Not relevant to a pouch except as a reason people come to pouches.

- "Trigger broke after second squirt" (B07HYP6D5C, 3 stars, 0 helpful)
- "Works great for a day. Does not last more than a day. You have to spray it everyday for it to work." (B07HYP6D5C, 3 stars, 0 helpful)
- "three AAA batteries last about 40 days. Making matters worse is the short overall lifespan, which is about a year before they stop working altogether." (B07N6JZ2J4, 3 stars, 1 helpful)
- "Might be nice if the pouches had strings attached to make it easier to secure in the engine compartment." (B0GMYLJSKV, 3 stars, 0 helpful)

### 2.17 Refund friction (3)

- Review title: "HOW DO I GET MY REFUND?" (B0DK9Y2LTR, 3 stars, 8 helpful)
- "Can i send back empty pouches?" (B0GMYLJSKV, 2 stars, 0 helpful)
- "Unfortunately, I’m like five days past my return window, so I probably won’t get a refund." (B0F62YTG6V, 1 star, 3 helpful)

One counter-example worth noting, because the reviewer forgave a product that failed: "Definitely does not work. Mice walk right across the bags as they are coming and going without even flinching but customer service is Amazing and they stand behind their product." (B0DK9Y2LTR, 3 stars, 0 helpful)

### 2.18 Trust: reviews, authenticity, ingredients, billing (10)

No critical reviewer says "the reviews are fake". They say they trusted the reviews:

- "I saw that these had a 4.1 star rating with so many positive reviews." (B07JMDYDVJ, 2 stars, 4 helpful)
- "Feel like I had bad luck after all these reviews." (B0FVLPXRNY, 2 stars, 0 helpful)
- "I am concerned that the manufacturer states that product sold on Amazon are knockoffs." (B0GMYLJSKV, 3 stars, 2 helpful)
- "My box also did not have the certification sticker to scan may have a lot to do with it" (B0FVLPXRNY, 3 stars, 0 helpful)
- Label reading: "I found it very strange that these instructions specifically state \"It is NOT the scent that repels rodents\"." (B07JMDYDVJ, 3 stars, 16 helpful, review titled "Snake oil, anyone?")
- Billing: "I never ordered a subscription and that is their scam, they will Continue to send this product at $147.00." (B0FVLPXRNY, 1 star, 5 helpful)
- Pack count, from a four-star review: "package says 10 pouches. Mine had only 8." (B07JMDYDVJ, 4 stars, 0 helpful)

---

## 3. Praise themes (base: 70 positive reviews; 50 once the 20 suspect Rodent Away reviews are set aside)

Read this section with care. The trustworthy positive base is 50 reviews from two products (Grandpa Gus's 30, Mighty Mint 20). Many are one line long.

| # | Theme | Count of 50 real | Share | Count in the 20 suspect |
|---|---|---|---|---|
| 1 | States a result: no mice, no signs, "it works" | 34 | 68% | 8 |
| 2 | Positive but with a caveat (fades, replace often, pricey, eaten pouches) | 12 | 24% | 0 |
| 3 | Strong scent taken as proof it must be working | 10 | 20% | 0 |
| 4 | Too early to tell, rated on hope | 10 | 20% | 0 |
| 5 | Repeat buyer, second winter or more | 9 | 18% | 0 |
| 6 | Pleasant smell, house smells fresh | 6 | 12% | 1 |
| 7 | Honest framing: deterrent, not a cure | 3 | 6% | 14 |
| 8 | Easy, nothing to set up | 3 | 6% | 12 |
| 9 | Pricing good | 2 | 4% | 0 |
| 10 | Mounting detail (2-sided tape, hanging string) | 1 | 2% | 2 |
| 11 | Safe around pets | 1 | 2% | 1 |

**What the happy buyers have in common.** The clearest result stories come from people protecting a closed, seasonally stored space **before** mice arrive: RVs, campers, motorhomes and trailers over winter (9 of the 50), plus garages and basements. They talk about prevention, they renew every season, and they do not expect the pouch to clear an active infestation. No positive reviewer describes pouches emptying a house that already had mice.

### 3.1 A stated result (34 of 50)

- "We put pockets in all our inside and outside compartments on our RV. No sign of rodents either place at the end of winter. Smell is pleasant and doesn’t linger after removing the packets." (B07JMDYDVJ, 5 stars, 12 helpful)
- "I have used this product for several years and never had a mouse problem in my camper. Just follow directions and u will have the same results." (B07JMDYDVJ, 5 stars, 0 helpful)
- "We haven't seen a field mouse in the two months we have been using them." (B0DK9Y2LTR, 5 stars, 0 helpful)
- "Better than expected. Put them down in specific areas and no more rodents." (B0DK9Y2LTR, 5 stars, 0 helpful)
- "I put these in the compartments by the openings and never did have any vermin enter and stay." (B07JMDYDVJ, 5 stars, 2 helpful)
- "Smell goes after a couple weeks. It did chase out a mouse in my garage" (B07JMDYDVJ, 4 stars, 2 helpful)
- "These packets come with 2-sided tape so they can be mounted under the hood. So far we aren't seeing any mice." (B0DK9Y2LTR, 5 stars, 3 helpful)
- The only measured result in the whole dataset sits in a three-star review: "So far so good. Started three weeks ago. Mouse droppings were =/- 25-30 per day. Day thirty 0-2." (B0GMYLJSKV, 3 stars, 1 helpful)

**How fast.** Almost nobody gives a speed. The stated horizons are "two months", "end of winter", "second year", "several years". The one fast claim is the garage mouse being chased out. Speed is not what delighted buyers praise; a quiet season is.

### 3.2 Positive with a caveat (12 of 50)

- "My only disappointment is they don't seem to work very long. BUT they DO work! Just replenish more often." (B0DK9Y2LTR, 4 stars, 2 helpful)
- "This product's ingredients appear to be effective in keeping mice out of my kitchen. The problem is its effectiveness does not last long (approximately 10 days)." (B07JMDYDVJ, 4 stars, 15 helpful)
- "Helped control mice problem Need to keep up with packet replacement" (B07JMDYDVJ, 4 stars, 0 helpful)
- "Works well but have to change out regularly for it to be effective." (B0DK9Y2LTR, 4 stars, 0 helpful)
- "our equipment in the barn seemed free of nests, however we did find some eaten pouches as well" (B07JMDYDVJ, 4 stars, 0 helpful)
- "Seems to work well. A little pricey." (B07JMDYDVJ, 4 stars, 0 helpful)

### 3.3 Strong scent as reassurance (10 of 50)

- "The smell is strong at first (sort of WAKES you up), but it's actually pleasant." (B0DK9Y2LTR, 5 stars, 32 helpful)
- "Has the house with a great smell. I can see why its repellent mice . The peppermint oil is strong." (B0DK9Y2LTR, 5 stars, 0 helpful)
- "They smell very strong so I'm hoping they last and work as advertised." (B07JMDYDVJ, 4 stars, 3 helpful)
- "It has a very strong smell at first of the natural ingredients/spices." (B07JMDYDVJ, 5 stars, 0 helpful)
- The dry counterpoint: "Strong peppermint odor for people and mice. Both seem to enjoy it." (B07JMDYDVJ, 4 stars, 0 helpful)

### 3.4 Too early, rated on hope (10 of 50)

- "So far no mice. Will know later as winter sets in." (B07JMDYDVJ, 4 stars, 0 helpful)
- "So far so good. Time will tell." (B07JMDYDVJ, 4 stars, 0 helpful)
- "I gave it 4 stars as it hasn't proven to work yet, meaning they haven't been in place long enough." (B07JMDYDVJ, 4 stars, 3 helpful)
- "As advertised, yet to decide if it works as stated." (B0DK9Y2LTR, 4 stars, 0 helpful)

A fifth of the "positive" reviews are from people who do not yet know. The category's star ratings are softer than they look.

### 3.5 Repeat buyers (9 of 50)

- "I use these in my trailer over the winter. This is my second year. Last year I had no mouse activity and hoping for a repeat this winter!" (B0DK9Y2LTR, 5 stars, 2 helpful)
- "This the second year we have used these and are using them again this year." (B07JMDYDVJ, 5 stars, 12 helpful)
- "We use these in our camper every year after closing it for the winter." (B07JMDYDVJ, 5 stars, 0 helpful)
- "As advertised and should do the job. They did last year." (B0DK9Y2LTR, 5 stars, 0 helpful)

### 3.6 Smell, safety, ease, small details

- "These make your house smell fresh and actually work." (B07JMDYDVJ, 5 stars, 6 helpful)
- "Smell much better than mothballs" (B07JMDYDVJ, 5 stars, 2 helpful)
- "This is one of the best, safest mouse repellents I have found." and "Safe around pets as well." (B07JMDYDVJ, 5 stars, 0 helpful)
- "Packets are a lot better than the spray." (B0DK9Y2LTR, 5 stars, 0 helpful)
- "it gives your house a nice smell, is easy to place, and avoids gruesome snap and sticky tracks" (B0DK9Y2LTR, 4 stars, 24 helpful)
- A direct request that matches our formula: "I would like the addition of cedar oil to the blend." (B0DK9Y2LTR, 5 stars, 0 helpful)

### 3.7 The suspect Rodent Away set (20 reviews, reported separately)

Their recurring points are tidy storage, easy placement, a hanging string, and an unusually careful insistence that a pouch is only one part of cleaning and sealing. Two lines show the pattern; treat them as marketing copy written by someone else, not as buyer speech:

- "The hanging string makes a lot more sense than something that needs to sit on the floor." (B0H7HY5CBT, 5 stars, 8 helpful)
- "In this fictional scenario, I'm a remote worker, and the setting is a home office with built-in cabinets." (B0H7HY5CBT, 5 stars, 0 helpful)

---

## 4. What buyers tried before or alongside (all 320 reviews; 45 mention another method)

| # | Method | Mentions | Note |
|---|---|---|---|
| 1 | Traps (snap, humane/live, glue) | 19 | 17 general or live, 2 glue |
| 2 | Peppermint oil or repellent sprays | 10 | |
| 3 | Cleaning, decluttering, food storage | 10 | 7 of these are in the suspect Rodent Away set; 3 elsewhere |
| 4 | Poison or bait | 4 | 2 used it, 2 refused it on principle |
| 5 | Cats | 2 | |
| 6 | Ultrasonic or plug-in devices | 1 in pouch reviews | plus the 20 ultrasonic reviews themselves |
| 7 | Other brands of pouch | 1 explicit | 2 more implied ("Just like everything else") |
| 8 | Exterminator / regular pest control | 1 | one more says a professional sealing the house is what it finally takes |
| 9 | Sealing entry holes | 1 did it | 2 more say they could not or had not yet |
| 10 | Powders, vinegar, mothballs, peppermint plug-ins | 1 each | |

The count is small because most reviews are short. What matters is how the methods relate: buyers reach for a scent repellent **after traps frustrate them or because they refuse poison**, and many then judge the pouch by putting it next to a trap.

**Traps: clever mice, mess, pets caught, and no stomach for killing**

- "They climb over the humane traps, avoid any of the food placed in them. So I heard to try mint." (B07JMDYDVJ, 2 stars, 4 helpful)
- "I tried glue traps, but was only able to catch my cat in them. So I definitely didn't want to try traditional snap traps." (B07JMDYDVJ, 2 stars, 0 helpful)
- "It runs past traps eight mouse killer and guess what it’s still here nothing has killed it." (B0FVLPXRNY, 2 stars, 0 helpful)
- "I first tried those humane mouse traps and put sunflower seeds as bait, the mouse knows something is going on and would not even give it a second look." (B0FVLPXRNY, 3 stars, 23 helpful)
- "I put these in my shop cause I had been seeing mice but haven’t caught any in my traps." (B0DK9Y2LTR, 3 stars, 0 helpful)
- "We had a mama & her babies that we couldn’t catch." (B0DDNSN224, 2 stars, 2 helpful)
- "Have caught 7 and released miles away alive." (B0FVLPXRNY, 2 stars, 0 helpful)

Traps are also what disappointed pouch buyers go back to: "I ended up getting rid of this rodent with a mouse trap with cheese." (B0DDNSN224, 1 star, 4 helpful) and "So I’m gonna just go with a sticky traps at this point" (B0DDNSN224, 2 stars, 6 helpful).

**Sprays and loose peppermint oil: gone in a day, endless re-spraying**

- "Been using the old bags to spray mint oil on them. Even the mint oils only last a short time." (B0DK9Y2LTR, 3 stars, 1 helpful)
- "Works great for a day. Does not last more than a day. You have to spray it everyday for it to work." (B07HYP6D5C, 3 stars, 0 helpful)
- "spray with peppermint oil under the hood at least every other day" (B07N6JZ2J4, 3 stars, 6 helpful)
- "some peppermint spray on paper towels (doesn’t work alone)" (B07N6JZ2J4, 3 stars, 2 helpful)
- "I also bought a spray that did not work, to spray inside the wheel wells to deter their entry into my car." (B07N6JZ2J4, 1 star, 17 helpful)

**Poison: refused because of pets, wildlife and children**

- "I didn't want to use any poisons because we live in the country and I didn't want to inadvertently kill any other animals." (B07JMDYDVJ, 2 stars, 6 helpful)
- "My neighbors mice have been trying to invade my storage space but I did not want to have pesticides around my dogs" (B0DDNSN224, 1 star, 11 helpful)
- "I love the smell and appreciate the fact that it is a repellent, not a poison." (B07JMDYDVJ, 2 stars, 0 helpful)
- One buyer used both: "I did how ever also placed bait traps under the skirted trailer to eliminate the mice altogether." (B07JMDYDVJ, 4 stars, 1 helpful)

**Ultrasonic and plug-in devices: nests built right beside them**

- "I promptly ordered 4 EverPest plug in devices and these pouches." (B0GMYLJSKV, 2 stars, 34 helpful)
- "Not only did it NOT scare the mouse. (Note: I had a trap in my car) It continued to eat from the traps I made." (B07N6JZ2J4, 1 star, 23 helpful)
- "Made sire batteries were charged and whatever it is still built a next right under it." (B07N6JZ2J4, 3 stars, 1 helpful)

**Other pouch brands**

- "Mighty Mint is the third brand of mouse repellent pouches I have tried over the years. Unfortunately, they aren’t much better than the previous two" (B0DK9Y2LTR, 3 stars, 1 helpful)

**Cats**

- "I have a cat who runs around and meows at the walls (lovely, smh)" (B07JMDYDVJ, 3 stars, 11 helpful)
- "I put them in my (mostly) finished basement because I no longer have a cat." (B0DK9Y2LTR, 5 stars, 32 helpful)

**Sealing and cleaning: known to be the real fix, often not possible yet**

- "I sprayed this and put it in the cracks of the house since it’s to cold to seal it up" (B07HYP6D5C, 3 stars, 0 helpful)
- "after I found and closed their entrance and been free of them inside for a month" (B0F62YTG6V, 1 star, 3 helpful)
- "Deep cleaned and treated every wood cabinet with vinegar mix and left out to dry." (B0FVLPXRNY, 2 stars, 0 helpful)

---

## 5. Where they use it (reviews that name a place)

153 of 320 reviews name at least one place. A review can name several. The second column removes the 20 suspect Rodent Away reviews.

| # | Location | All 320 | Without suspect set |
|---|---|---|---|
| 1 | House in general ("around the house", apartment, counters, rooms) | 31 | 30 |
| 2 | Car or truck (engine bay, cabin, trunk) | 25 | 24 |
| 3 | Outdoors (yard, garden, burrows, porch, fences) | 24 | 24 |
| 4 | RV, camper, motorhome, trailer | 17 | 17 |
| 5 | Garage | 16 | 12 |
| 6 | Kitchen and pantry (kitchen 12, pantry 4) | 16 | 15 |
| 7 | Shed, shop building, barn, feed room, tack locker | 14 | 12 |
| 8 | Closets and storage rooms | 9 | 5 |
| 9 | Basement | 5 | 4 |
| 10 | Attic | 3 | 1 |
| 11 | Bathroom, bedroom | 3 each | 2 each |
| 12 | Hunting or deer blind | 2 | 2 |
| 13 | Greenhouse | 2 | 1 |
| 14 | Cabin, crawlspace, office, laundry, mudroom | 1-2 each | cabin 1, crawlspace 1 |

Notes:

- Car counts are inflated by the ultrasonic product (14 of the 25). Among pouch reviews only: house 26, outdoors 19, RV/camper 15, garage 12, kitchen 11, car 10, shed 7.
- **RV and camper is the happiest location.** 9 of the 17 RV mentions are in positive reviews. **Outdoors is the unhappiest:** all 24 outdoor mentions are critical, nearly all about the wrong animal or open air.
- Attic and basement, which a page might assume are core uses, are barely mentioned by real buyers.
- Reviewers themselves see enclosure as the deciding factor: "So this might work in your enclosed garage, but for outdoors it has been not effecive for me" (B0FVLPXRNY, 3 stars, 23 helpful) and "it may work better in a smaller or more enclosed environment" (B07JMDYDVJ, 3 stars, 4 helpful).

---

## 6. The buyer's own words

All phrases are exact, taken from real (non-suspect) reviews. ASIN and star rating follow each.

### The problem: hearing, seeing, smelling, damage, fear

1. "Didn't hear them in the walls anymore until within 1 month we are hearing them again" (B0GMYLJSKV, 2)
2. "still hear mice" (B07JMDYDVJ, 3)
3. "I have a cat who runs around and meows at the walls" (B07JMDYDVJ, 3)
4. "our present kitchen mouse still comes out from behind the stove at some point during the night" (B0DK9Y2LTR, 3)
5. "Had a horrific overnight fall invasion of mice." (B0FVLPXRNY, 2)
6. "I am now finding droppings literally inches away from the peppermint" (B0FVLPXRNY, 2)
7. "it was mouse poop all around it" (B0FVLPXRNY, 2)
8. "LEGIT RAT POOP ALL OVER THESE THING" (B0DDNSN224, 1)
9. "Saw turds 4 days later." (B0DK9Y2LTR, 3)
10. "I recently discovered mouse droppings in my pantry cupboard" (B0GMYLJSKV, 2)
11. "evidence of the unwanted house guests" (B0FVLPXRNY, 2)
12. "unwanted furry roommates" (B07HYP6D5C, 3)
13. "they’re still hanging around like they pay rent" (B07HYP6D5C, 3)
14. "It’s like it’s smart and it’s like this is my house you get out" (B0FVLPXRNY, 2)
15. "the mice that have taken up residency in our garage" (B07JMDYDVJ, 2)
16. "I still have a little critter running around my house" (B07JMDYDVJ, 3)
17. "a mama & her babies that we couldn’t catch" (B0DDNSN224, 2)
18. "My neighbors mice have been trying to invade my storage space" (B0DDNSN224, 1)
19. "They still broke in and ate my hamburger buns" (B0DDNSN224, 1)
20. "Deer mice are the ones known to possibly carry the deadly virus we’ve been hearing about on the news" (B0GMYLJSKV, 2)
21. "a family of mouse repopulating and running around in my car" (B07N6JZ2J4, 1)
22. "a nest of newly born mice in my air cabin filter" (B07N6JZ2J4, 3)
23. "huge repair bills for wiring damage due to rodents under the hood of my vehicle" (B07N6JZ2J4, 3)
24. "chewed up one of the engine wiring harness’s at a cost of almost $600" (B07N6JZ2J4, 1)
25. "started chewing the leather seats" (B07N6JZ2J4, 3)
26. "They have to go before they burn my cabin down." (B0GMYLJSKV, 2)
27. "this year there has been a mouse explosion around here" (B07N6JZ2J4, 3)
28. "Today’s mice have a game plan to keep warm and fed in winter." (B07JMDYDVJ, 4)
29. "Getting cold outside so we'll see when the mice are looking for a cozy spot" (B0DK9Y2LTR, 3)
30. "It about knocks me out when I walk in the house and reminds me of the mouse issue." (B0F62YTG6V, 1)

### The wish: what success sounds like

31. "I really want to prevent rather than trap." (B07JMDYDVJ, 4)
32. "No sign of rodents either place at the end of winter." (B07JMDYDVJ, 5)
33. "never had a mouse problem in my camper" (B07JMDYDVJ, 5)
34. "So far I have found no new mouse droppings" (B0DK9Y2LTR, 3)
35. "Put them down in specific areas and no more rodents." (B0DK9Y2LTR, 5)
36. "Last year I had no mouse activity and hoping for a repeat this winter!" (B0DK9Y2LTR, 5)
37. "pack their little bags and leave for good" (B07HYP6D5C, 3)
38. "I just knew I found a solution to my problem." (B07JMDYDVJ, 2)
39. "I think the key with pest control is getting ahead of the problem." (B0DK9Y2LTR, 5)
40. "better safe than sorry" (B07JMDYDVJ, 5)
41. "I do not want to kill them but I am running out of options." (B0GMYLJSKV, 2)
42. "avoids gruesome snap and sticky tracks" (B0DK9Y2LTR, 4)
43. "I was (and am) desperate to keep those little devils away" (B07N6JZ2J4, 3)
44. "Still much less trouble and certainly less expensive than replacing a wiring harness." (B07N6JZ2J4, 3)
45. "Still looking for something that works." (B07N6JZ2J4, 1)
46. "Was hoping they’d work for a lot longer." (B0FVLPXRNY, 3)
47. "I did not think a month was my idea of rodent control." (B0F62YTG6V, 3)

### The doubts: before buying and while waiting

48. "Who knows if they are working?" (B0GMYLJSKV, 3)
49. "How does one know?" (B07JMDYDVJ, 4)
50. "not really sure how to tell if these are really doing anything" (B0GMYLJSKV, 3)
51. "Just like everything else." (B0DK9Y2LTR, 3)
52. "Snake oil, anyone?" (B07JMDYDVJ, 3, review title)
53. "Maybe I have resistant mice." (B0GMYLJSKV, 3)
54. "Maybe these aren't for every mouse lol." (B07JMDYDVJ, 2)
55. "Peppermint doesn't work on rats, or mouse." (B0DDNSN224, 2)
56. "Just hope it was worth the price…." (B07JMDYDVJ, 3)
57. "I had high hopes tho" (B07JMDYDVJ, 2)
58. "Feel like I had bad luck after all these reviews." (B0FVLPXRNY, 2)
59. "I'm not convinced these work." (B07N6JZ2J4, 3)
60. "If it doesn't work in a 10 sq ft closet it won't work in the garage or shed." (B07JMDYDVJ, 2)
61. "Does it have to be repeated ?? Does anyone know??" (B07JMDYDVJ, 4)
62. "This is a deterrent not a solution." (B0DK9Y2LTR, 5)
63. "Not sure if it’s a state to state thing" (B0DDNSN224, 1)
64. "Maybe I need to add more?" (B0FVLPXRNY, 3)

---

## 7. Expectations versus reality

### What they believed it would do

- **Clear out mice that are already inside.** Most critical buyers bought with mice present and expected departure. "No mice came running out." (B0GMYLJSKV, 3 stars) and the review title "No dead mice found yet. They aren't drawn to it or do like it. Disappointed." (B0DK9Y2LTR, 3 stars) show two buyers who expected a visible exodus or even a kill.
- **Form a barrier mice will not cross.** Hence the shock at mice beside, on or carrying the pouch: "Mice walk right across the bags as they are coming and going without even flinching" (B0DK9Y2LTR, 3 stars).
- **Last as long as the label says.** "these Sofyre pouches should be at maximum strength at the moment since they’re advertised to last for up to 90 days" (B0GMYLJSKV, 2 stars, 34 helpful). This is the same 90-day claim our product makes, judged a failure on day 5.
- **Work on any rodent or small pest.** Groundhogs, squirrels, chipmunks, moles, raccoons, spiders, ants, crickets, wasps, even a pet rabbit.
- **Work in open air** (yards, patios, deer blinds, greenhouses, a 30 by 40 foot shop).
- **Be a one-off purchase.** Monthly replacement came as an unwelcome surprise to several.

### How long they gave it before judging

Stated times to verdict, from the reviews that give one (roughly 45):

| Time given | Examples |
|---|---|
| Same day to next morning | "Today is 1st day"; "back the same evening"; "the next morning there was mouse poop next to it"; "twenty-four hours later" |
| 2 to 5 days | "Only work for about 2 days"; "after only 3 days"; "Saw turds 4 days later"; "after only 5 days of use"; "Maybe worked five days" |
| About a week | "for the first week"; "about 7 days"; "about a week or so" |
| 10 days to 3 weeks | "about 10 days"; "a week and a half"; "a couple of weeks"; "three weeks ago" |
| About a month | "within 1 month"; "almost a full 30 days"; "for about a month" |
| A season or more | Only in positive reviews: "end of winter", "second year", "several years" |

Most negative verdicts land inside the first week. A single sighting or one fresh dropping is enough: "I placed one bag on the counter and the next morning there was mouse poop next to it." Nobody describes a product telling them what to expect in week one.

### How many they placed, in what space

- 12 pouches in an 1,100 sq ft apartment (about 1 per 92 sq ft), still seeing mice at three weeks (B0DK9Y2LTR)
- 12 bags in a 30 by 40 ft shop building (1 per 100 sq ft), "ZERO EFFECT" (B0DDNSN224)
- 2 pouches in a 17.5 sq ft shed, chewed and nested on within 24 hours (B07JMDYDVJ)
- 2, then 3 pouches in a 10 sq ft water-heater closet, droppings after 3 days (B07JMDYDVJ)
- A whole pack "in a 3’ x 3’ area", two mice walked in at three weeks (B0DDNSN224)
- 3 under a car hood, rodents back within days (B07JMDYDVJ)
- 4 in a garage, "Still see mice" (B0FVLPXRNY)
- 1 used, "saw no results" (B0GMYLJSKV)
- 1 on a kitchen counter (B0DDNSN224); 2 in one drawer (B0F62YTG6V); 1 each side of the stove and 1 under the drawer (B0DK9Y2LTR)
- 3 in a shed, "(maybe one is enough )" (B0F62YTG6V); too many under a house, causing a migraine (B07JMDYDVJ)
- "we followed and in fact exceeded the recommendations for number of packets per square foot" in a greenhouse (B07JMDYDVJ)

Two things follow. First, failures are reported at densities **well above** label coverage (two pouches in 17.5 sq ft), so "use more" is not an answer buyers will accept. Second, buyers have no shared idea of the right number: the same reviews range from one pouch for a house to a full pack in nine square feet.

---

## 8. Unmet needs: what the unhappy buyers were really asking for

1. **A way to know it is working.** The absence of mice is invisible, so buyers either guess or test it against a trap. "How does one know? I marked calendar for 30 days." No product gave them a check: what to look for, by when, and what to do if they still see signs. The one buyer who counted droppings (25-30 a day down to 0-2) is the only one who sounds sure.

2. **Scent life that matches the claim, in their own nose.** They want months and get days. "I did not think a month was my idea of rodent control." They also use their own sense of smell as the gauge, so a pouch that still works but no longer smells strong to a person reads as dead. Nobody tells them when to replace or how to tell.

3. **A pouch a mouse cannot chew, carry off or nest on.** The fabric sachet is treated as bedding or a toy. "she built a nest on top of one of them." Buyers who watched a pouch get dragged away never come back. No product in this set offers a chew-resistant housing or a way to fix the pouch in place, apart from Mighty Mint's tape, which is praised.

4. **An honest answer for mice that are already inside.** Most critical buyers had an active problem and no plan beyond the pouch. They wanted to be told what a repellent can and cannot do against resident mice, and what to pair it with. "Maybe use these along side other repellents, but these aren’t enough by themselves."

5. **Clear dosing and placement.** How many for this room, where exactly, how close to the entry point. "it seems that I would have to have these pouches laid out everywhere at a one foot spacing". Over-use produced migraines; under-use produced "one pouch, no results".

6. **A smell strong enough for mice and liveable for people, that is what the label says.** B0F62YTG6V shows what happens when "peppermint" arrives smelling of mothballs: 15 complaints in 30 reviews. On the other side, one buyer held a Grandpa Gus's sachet to her nose and wondered if it had expired. Buyers want consistent, recognisable peppermint, and guidance on rooms where people sleep.

7. **Kill-free and pet-safe, without contradictions.** People choose this category to avoid poison and gruesome traps. Then they meet a box that says "keep away from pets and children" under a listing that says safe for both, or a vet who warns about essential oils and pets. They want one straight, specific statement, including birds and cats.

8. **Clarity on which animals it is for.** "If it not meant for groundhogs may be it would be a good idea to make it clear on package." A seventh of all critical reviews come from people who should never have bought it.

9. **Protection for parked vehicles and stored RVs that stays put.** "Might be nice if the pouches had strings attached to make it easier to secure in the engine compartment." These buyers carry the highest stakes in the data ($600 wiring harness, chewed seats, nests on the engine) and are the most loyal when it works.

10. **A cost that makes sense per month of protection.** The price complaint is always price divided by days of smell. "Too much money for that short time ."

11. **A refund that is still open when they find out.** Three buyers hit the Amazon return window before they could judge. "The return window is nearly up, and I am still seeing mice." The one brand that handled a failure well kept three stars from a customer who says it "Definitely does not work".

---

## 9. Honesty: repels, does not remove; works with sealing and cleaning

This matters for our page. The most-upvoted and most thoughtful reviews in the dataset, critical and positive alike, are the ones that say a scent repellent deters and does not evict. Buyers reward that framing with helpful votes and punish its absence with one-star reviews.

**It deters newcomers; it does not clear an existing infestation**

- "I believe they work better to deter mice or ants from coming in but if they are already there not so much. A good prevention product." (B0DK9Y2LTR, 3 stars, 3 helpful)
- "With that said if you have an infestation this probably wouldn't be helpful; maybe combined with traps it would help a little but not a solution. This is a deterrent not a solution." (B0DK9Y2LTR, 5 stars, 32 helpful)
- "It’s not a total loss—it's definitely reduced the number of mouse sightings, and I feel like they’re annoyed by the smell, just not enough to pack their little bags and leave for good." and "Just don’t expect a full-blown rodent eviction" (B07HYP6D5C, 3 stars, 108 helpful, the most-upvoted review in the dataset)
- "They do help but do not get the mice out for good." under the title "They are a help but not the solution." (B0DK9Y2LTR, 3 stars, 2 helpful)
- "I did give it 3 stars because it maybe would work in a vehicle that never had mice in it." (B07N6JZ2J4, 3 stars, 0 helpful)
- "they did reduce the rodent droppings under the hood, but not completely" (B07N6JZ2J4, 3 stars, 6 helpful)

**It moves them rather than removes them**

- "Ya they repel them to somewhere else in the shed lol." (B07JMDYDVJ, 3 stars, 0 helpful)
- "They will repel mice but the mice might find new spots to get in. Just buy more." (B07JMDYDVJ, 5 stars, 6 helpful)
- "That means if you put it in a corner that breaks their path, they might go elsewhere." (B0DK9Y2LTR, 4 stars, 24 helpful)

**It only works alongside sealing, cleaning and food storage**

- "Kinda worth it if you're needing to get rid of mouse quickly and you can get to sealing the gaps but for long term, mehhhh..." (B07JMDYDVJ, 3 stars, 13 helpful)
- "good but not as a standalone repellent: good housekeeping and food containment practices are essential - and perhaps these might help, but they do not provide a standalone repellent." (B07JMDYDVJ, 2 stars, 0 helpful)
- "a long term solution likely requires having a professional find the points of access to your home and sealing them off" (B0DK9Y2LTR, 4 stars, 24 helpful)
- "The catch: It won't last forever, and they will come back... eventually." (B0DK9Y2LTR, 4 stars, 24 helpful)
- "Maybe use these along side other repellents, but these aren’t enough by themselves." (B0DK9Y2LTR, 2 stars, 0 helpful)
- "I did how ever also placed bait traps under the skirted trailer to eliminate the mice altogether." (B07JMDYDVJ, 4 stars, 1 helpful)

**Hungry or established mice will push through a smell**

- "Maybe I have some very desperate and hungry critters in my apartment who just don’t care and will endure multiple forms of torture for a meal ? ?" (B0GMYLJSKV, 2 stars, 34 helpful)
- "I am not sure if the mice get used to the scent or if the scent dissipates so quickly, but I found mouse poop on several of the sachets." (B07JMDYDVJ, 2 stars, 0 helpful)
- "Not sure if they got used to the scent" (B07HYP6D5C, 2 stars, 26 helpful)

**The suspect Rodent Away reviews lean hard on the same message.** 14 of the 20 say some version of "a scent product cannot repair a damaged door or a hole in a wall" (B0H7HY5CBT, 5 stars, 1 helpful, a self-declared "fictional scenario"). Whoever wrote them judged that modest claims read as more believable in this category. That is a signal about competitor positioning, not customer testimony.

### What this means for our page

- The claims most exposed by this data are the ones on our own label: **"up to 90 days"** and **"covers about 65 sq ft"**. Competitor buyers report scent life of days to a month and failures at far higher density than one pouch per 65 sq ft. If we state these numbers, we should say what they are based on, say that the smell a person notices fades before the pouch is spent (if that is true of our castor-oil base), and say when to replace.
- Do not promise removal of an existing infestation. The reviews that set this expectation honestly earn the most helpful votes; the products that let buyers assume it collect "mouse sat right next to it".
- Say plainly that it is for mice, name the animals it is not for, and say it is for enclosed spaces rather than open yards. That alone would have prevented about one in seven of the critical reviews here.
- Lead with the use that actually delights people: protecting a closed space before winter (RV, camper, garage, stored vehicle), renewed each season.
- Pair it openly with sealing gaps, food storage, and traps for mice already inside. Buyers already believe this; a page that says it first sounds like the honest reviewer, not the listing.
- Our 90-day money-back guarantee answers a real, stated pain: the Amazon return window closing before a buyer can judge.
