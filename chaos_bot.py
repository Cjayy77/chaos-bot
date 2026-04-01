"""
🌀 Chaos Bot — No AI, Pure Mayhem
A social chaos bot with zero AI, zero theme, maximum unhinged energy.

Commands:
  !rate <thing>    - Rate anything out of 10
  !fact            - Drop a cursed/weird fact
  !dare            - Get a random dare or challenge
  !event           - Trigger a random server event
  !ball <question> - Unhinged magic 8ball
  !debate          - Drop a random debate topic
  !chaos           - Show all commands
"""

import discord
from discord.ext import commands
import random
import hashlib
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ── Facts ──────────────────────────────────────────────────────────────────────
CURSED_FACTS = [
    "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
    "A group of flamingos is called a flamboyance. You're welcome.",
    "Humans share 60% of their DNA with bananas. Some more than others.",
    "The inventor of the Frisbee was turned into a Frisbee after he died. His family had him cremated and made into one.",
    "Wombats produce cube-shaped poop. No other animal on Earth does this.",
    "There are more possible games of chess than atoms in the observable universe.",
    "The average person walks past 36 murderers in their lifetime. Sleep well.",
    "Oxford University is older than the Aztec Empire.",
    "Crows hold grudges. They remember faces. They tell their friends. Be careful.",
    "A shrimp's heart is in its head.",
    "Lobsters are biologically immortal. They just get killed before they die.",
    "The word 'nerd' was first used in a Dr. Seuss book in 1950.",
    "Snails can sleep for 3 years straight.",
    "Cats have a special vocalization they only use with humans. They invented it to manipulate us.",
    "The blob of toothpaste on a toothbrush is called a 'nurdle'.",
    "France was still executing people by guillotine when Star Wars came out.",
    "A day on Venus is longer than a year on Venus.",
    "Otters hold hands while sleeping so they don't drift apart. Meanwhile you're alone.",
    "The average cloud weighs about 1.1 million pounds.",
    "Humans are the only animals that blush. Make of that what you will.",
    "Nintendo was founded in 1889. They sold playing cards.",
    "The smell of rain has a name: petrichor. The smell of nothing: your future.",
    "Billy goats urinate on their own heads to smell more attractive.",
    "Mosquitoes have killed more humans than all wars combined.",
    "A single strand of spaghetti is called a spaghetto.",
    "Penguins propose with pebbles. More romantic than most humans.",
    "The 't' in 'hashtag' is silent apparently. People say 'hashTAG' wrong. Just kidding. But think about it.",
    "Banging your head against a wall burns 150 calories per hour.",
    "There are more trees on Earth than stars in the Milky Way.",
    "Every time you shuffle a deck of cards, the order has almost certainly never existed before.",
    "The voices of Mickey Mouse and Minnie Mouse got married in real life.",
    "A group of pugs is called a grumble.",
    "In Switzerland, it's illegal to own just one guinea pig because they get lonely.",
    "The longest English word you can type with only the left hand is 'stewardesses'.",
    "Pineapples take about 2 years to grow. You eat it in 3 minutes.",
    "Sea otters have a favorite rock they keep in a pocket of skin. For their whole life.",
    "Humans are the only animals that cook food. Fire: the original life hack.",
    "A blue whale's heart is so big, a human could crawl through its arteries.",
    "The word 'quarantine' comes from 40 days of isolation. 'Quaranta' = forty in Italian.",
    "Koalas have fingerprints nearly identical to humans. Cold case investigators hate this.",
    "When you get a kidney transplant, they usually leave your original kidneys in.",
    "The electric chair was invented by a dentist.",
    "Hippopotamus milk is pink.",
    "Ancient Egyptians shaved off their eyebrows when their cat died.",
    "A group of cats is called a clowder. A group of kittens is called a kindle.",
    "There are more fake flamingos in the world than real ones.",
    "The inventor of the Pringles can is buried in one.",
    "Competitive art used to be an Olympic sport. Paintings, sculptures, music.",
    "It rains diamonds on Neptune and Uranus.",
    "You cannot hum while holding your nose closed.",
]

# ── Dares ──────────────────────────────────────────────────────────────────────
DARES = [
    "Send a voice message saying 'I am the night' in the deepest voice you can.",
    "Change your nickname to something embarrassing for the next hour.",
    "Text the 5th person in your contacts 'we need to talk' and screenshot their reply.",
    "Post your most recent Google search in the chat.",
    "Do 20 jumping jacks and voice note it.",
    "Type with your elbows for the next 5 messages.",
    "Send a handstand photo. You have 10 minutes.",
    "Describe your personality as a food. No take-backs.",
    "Write a haiku about the last thing you ate. Right now.",
    "Post your camera roll photo from exactly one year ago today.",
    "Set your status to 'I am the main character' for the rest of the day.",
    "Explain quantum physics in exactly 10 words.",
    "Post your most embarrassing autocorrect fail.",
    "React to every message in this server for the next 2 minutes.",
    "Send a singing voice message. Any song. No excuses.",
    "Describe yourself using only movie titles.",
    "Post the last meme you sent to someone.",
    "Write a 5-star review of water.",
    "Introduce yourself as if you're a medieval knight.",
    "Explain your job/school using only emojis.",
    "Change your avatar to a potato for 24 hours.",
    "Type everything in reverse for the next 3 messages.",
    "Send a voice message doing your best impression of a robot.",
    "Post the 7th photo in your phone gallery. No deletions allowed.",
    "Write a breakup letter to your least favorite food.",
    "Give a Ted Talk about socks. You have 60 seconds.",
    "Send a formal business email to the last person you texted.",
    "Invent a new word and use it in a sentence.",
    "Post a childhood photo. The rules are non-negotiable.",
    "Pretend you're a news anchor and report on your current location.",
]

# ── Server events ──────────────────────────────────────────────────────────────
EVENTS = [
    "🎰 **LOTTERY TIME** — First person to type their lucky number wins absolutely nothing but eternal glory.",
    "🏆 **SPONTANEOUS COMPETITION** — Who can send the most creative sentence using only 5 words? Go.",
    "🎭 **ROLE REVERSAL** — Everyone must explain what they think the person above them does for a living.",
    "🔮 **PROPHECY HOUR** — Everyone predict something that will happen in this server within 24 hours.",
    "🎪 **CHAOS AUCTION** — Auction off something you own using only emoji as currency.",
    "📸 **PHOTO CHALLENGE** — First person to post a photo of something red wins the title of Champion.",
    "🎵 **SONG DUEL** — Name a song that matches the current vibe of this server. Best one wins.",
    "🌀 **RANDOM ALLIANCE** — The next two people to talk are now allies for the rest of the day.",
    "🎯 **TRIVIA SPRINT** — What country has the most time zones? First correct answer wins.",
    "💀 **ELIMINATION ROUND** — Everyone say one controversial opinion. Most upvoted survives.",
    "🔥 **HOT SEAT** — Next person to talk gets roasted by everyone else. You've been warned.",
    "🧠 **BRAIN BATTLE** — First person to name 5 countries without the letter 'a' wins undying respect.",
    "🎲 **DICE DUEL** — Everyone pick a number 1-6. Most people who picked the same number wins.",
    "👑 **KINGMAKER** — Someone must declare a temporary king/queen of the server. Power lasts 10 minutes.",
    "🌊 **WAVE OF CHAOS** — Everyone change their nickname to a sea creature for 30 minutes.",
    "📖 **STORY TIME** — Build a story one sentence at a time. First person who breaks the plot loses.",
    "🎭 **IMPRESSION CONTEST** — Impersonate another server member in text. Others guess who.",
    "⚡ **SPEED ROUND** — First person to type the alphabet backwards wins. Partial credit for effort.",
    "🦆 **RUBBER DUCK SYNDROME** — Everyone must explain their current problem to a rubber duck. Post results.",
    "🎪 **TALENT SHOW** — Share a weird talent you have. No skill too small or too cursed.",
]

# ── 8ball ──────────────────────────────────────────────────────────────────────
BALL_RESPONSES = [
    "absolutely not and you should feel bad for asking",
    "the stars say yes but the stars have been wrong before",
    "my lawyer has advised me not to answer that",
    "ask again after you've had a glass of water",
    "that is literally none of my business but yes",
    "the answer is yes and you will regret it",
    "signs point to no but signs have been wrong",
    "lol no",
    "yes but not for the reasons you think",
    "I consulted three different sources and they all said maybe",
    "the universe says yes but the universe is chaotic and unreliable",
    "no, and please stop",
    "technically yes but morally questionable",
    "my sources are conflicted. flip a coin. ignore the result.",
    "I don't know but I'm judging you for asking",
    "yes if you're brave enough. you're not.",
    "ask your enemies. they know the truth.",
    "the answer is somewhere between yes and absolutely not",
    "this question has no good answer. proceed anyway.",
    "only on Tuesdays",
    "not with that attitude",
    "I've seen worse ideas. not many, but some.",
    "the prophecy is unclear but the vibes are off",
    "yes, unfortunately",
    "no, fortunately",
    "that depends. are you prepared for the consequences?",
    "I'm going to pretend you didn't ask that",
    "somehow both yes and no simultaneously",
    "ask me again and I'll give you the same answer",
    "the real answer was the friends we made along the way",
]

# ── Debates ────────────────────────────────────────────────────────────────────
DEBATES = [
    "Is a hot dog a sandwich? There is a correct answer and you are probably wrong.",
    "Pineapple on pizza: culinary crime or misunderstood genius?",
    "Is water wet? Be specific. Defend your answer.",
    "If you could only eat one food forever, what would it be and why are you wrong?",
    "Is cereal a soup? Milk is broth. Cereals are ingredients. Fight me.",
    "Which is worse: slow WiFi or no WiFi?",
    "Would you rather have no fingers or no toes? Think carefully.",
    "Is a staircase going up or going down?",
    "Does a straw have one hole or two?",
    "Should toilet paper go over or under? There is a wrong answer.",
    "Is it possible to hum with your mouth open? Try it. Now debate.",
    "If you could uninvent one thing, what would it be?",
    "Are eyebrows facial hair?",
    "Is a burger still a burger if you remove the bun?",
    "Which came first: the chicken or the egg? No philosophy allowed. Pick one.",
    "Is driving 5mph over the speed limit morally acceptable?",
    "Do you think fish get thirsty?",
    "Is a push notification from an app a form of communication?",
    "Could you survive longer without your phone or without shoes?",
    "Is it rude to recline your airplane seat?",
    "At what point does a pile of sand become a sand pile?",
    "Is a DJ a musician?",
    "Should you put butter on both sides of the bread for a grilled cheese?",
    "Would you rather know how you die or when you die?",
    "Is a taco a sandwich? Use the sandwich theorem.",
    "If you punch yourself and it hurts, are you strong or weak?",
    "Is there a difference between love and very strong like?",
    "Should fonts have feelings? Comic Sans disagrees.",
    "Is glass a liquid or a solid? It's complicated. Debate.",
    "What's heavier: a pound of feathers or a pound of bricks? Wrong answers only.",
    "Is sleep just a really long blink?",
    "Would you rather fight 100 duck-sized horses or 1 horse-sized duck?",
    "Are stairs just a ramp with commitment issues?",
    "Is a cloud just fog that doesn't know where it's going?",
    "Could Batman beat Superman if he had enough time to prepare? How much time?",
]

# ── Rating system ──────────────────────────────────────────────────────────────
RATING_COMMENTS = {
    (0, 1):   ["absolutely cursed", "did not survive the vibe check", "deleted from my memory", "I'm calling someone"],
    (2, 3):   ["needs serious work", "exists I guess", "C- at best", "room for improvement is an understatement"],
    (4, 5):   ["mid. capital M. Mid.", "exactly average and that's somehow offensive", "exists in the grey zone", "fine I guess"],
    (6, 7):   ["not bad actually", "passing the vibe check", "got potential", "decent, I've seen worse"],
    (8, 9):   ["lowkey fire", "actually slaps", "went off", "genuinely impressive"],
    (10, 10): ["PEAK", "the greatest thing ever submitted to this server", "we don't deserve it", "history has been made"],
}

def get_rating_comment(score: int) -> str:
    for (low, high), comments in RATING_COMMENTS.items():
        if low <= score <= high:
            return random.choice(comments)
    return "indescribable"

def deterministic_rate(thing: str) -> int:
    """Same input always gets same score — feels consistent, not random."""
    return int(hashlib.md5(thing.lower().strip().encode()).hexdigest(), 16) % 11


# ── Events ─────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"🌀 Chaos Bot online as {bot.user}")
    await bot.change_presence(activity=discord.Game("!chaos • Pure Mayhem"))


# ── Commands ───────────────────────────────────────────────────────────────────
@bot.command(name="chaos", help="Show all commands.")
async def chaos(ctx):
    embed = discord.Embed(
        title="🌀 Chaos Bot",
        description="No AI. No theme. Pure unhinged energy.",
        color=0xFF4500,
    )
    for name, val in [
        ("`!rate <anything>`", "Rate literally anything out of 10"),
        ("`!fact`",            "Get a cursed or weird fact"),
        ("`!dare`",            "Get a random dare or challenge"),
        ("`!event`",           "Trigger a random server event"),
        ("`!ball <question>`", "Consult the unhinged magic 8ball"),
        ("`!debate`",          "Drop a random debate topic"),
    ]:
        embed.add_field(name=name, value=val, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="rate", help="Rate anything out of 10. Usage: !rate pizza")
async def rate(ctx, *, thing: str = ""):
    if not thing:
        await ctx.send("❌ Rate what exactly? Give me something. `!rate <thing>`")
        return
    score = deterministic_rate(thing)
    comment = get_rating_comment(score)
    bar = "█" * score + "░" * (10 - score)
    embed = discord.Embed(
        title=f"📊 Official Rating",
        color=0xFF4500,
    )
    embed.add_field(name="Subject", value=f"**{thing}**", inline=False)
    embed.add_field(name="Score", value=f"**{score}/10** — {comment}", inline=False)
    embed.add_field(name="Bar", value=f"`{bar}`", inline=False)
    embed.set_footer(text="These results are final and legally binding.")
    await ctx.send(embed=embed)


@bot.command(name="fact", help="Get a cursed or weird fact.")
async def fact(ctx):
    f = random.choice(CURSED_FACTS)
    embed = discord.Embed(
        title="🧠 Cursed Fact",
        description=f,
        color=0x9B59B6,
    )
    embed.set_footer(text="You can't unknow this now.")
    await ctx.send(embed=embed)


@bot.command(name="dare", help="Get a random dare or challenge.")
async def dare(ctx):
    d = random.choice(DARES)
    embed = discord.Embed(
        title="🎯 Your Dare",
        description=f"**{d}**",
        color=0xE74C3C,
    )
    embed.set_footer(text="No skipping. No excuses. Good luck.")
    await ctx.send(embed=embed)


@bot.command(name="event", help="Trigger a random server event.")
async def event(ctx):
    e = random.choice(EVENTS)
    embed = discord.Embed(
        title="⚡ SERVER EVENT",
        description=e,
        color=0xF1C40F,
    )
    embed.set_footer(text=f"Triggered by {ctx.author.display_name} • Participation is mandatory.")
    await ctx.send(embed=embed)


@bot.command(name="ball", help="Consult the unhinged 8ball. Usage: !ball will I win?")
async def ball(ctx, *, question: str = ""):
    if not question:
        await ctx.send("❌ Ask a question. `!ball <question>`")
        return
    response = random.choice(BALL_RESPONSES)
    embed = discord.Embed(
        title="🎱 The Ball Has Spoken",
        color=0x2C3E50,
    )
    embed.add_field(name="Question", value=f"*{question}*", inline=False)
    embed.add_field(name="Answer", value=f"**{response}**", inline=False)
    embed.set_footer(text="The ball is not responsible for any decisions made.")
    await ctx.send(embed=embed)


@bot.command(name="debate", help="Drop a random debate topic.")
async def debate(ctx):
    d = random.choice(DEBATES)
    embed = discord.Embed(
        title="🔥 Debate Topic",
        description=f"**{d}**",
        color=0xFF6B00,
    )
    embed.set_footer(text="No neutral answers. Pick a side.")
    msg = await ctx.send(embed=embed)
    try:
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
    except Exception:
        pass


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise ValueError("Set the DISCORD_TOKEN environment variable.")
    bot.run(token)
