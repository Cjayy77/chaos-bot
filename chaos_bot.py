"""
🌀 Chaos Bot — No AI, Pure Mayhem

Passive systems (automatic):
  🎭 Personality shifts  — bot changes personality every 3 hours
  👁️ The Watcher        — randomly interrupts chat (~4% per message)
  ⚔️ Server Wars        — auto declares daily rivalries
  🌡️ Chaos Meter        — fills with activity, unleashes chaos at 100%
  📜 Lore builder       — silently collects lore on members

Commands:
  !rate <thing>    - Rate anything out of 10
  !fact            - Drop a cursed fact
  !dare            - Get a dare
  !event           - Trigger a server event
  !ball <question> - Unhinged magic 8ball
  !debate          - Random debate topic
  !roulette        - Spin the chaos roulette (unknown outcome)
  !lore [@user]    - Read someone's lore entry
  !cursedpoll      - Drop a cursed poll (all options are bad)
  !war             - Check current server war status
  !meter           - Check the chaos meter
  !chaos           - Show all commands
"""

import discord
from discord.ext import commands, tasks
import random
import hashlib
import os
import datetime
from collections import defaultdict

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ── State ──────────────────────────────────────────────────────────────────────
chaos_meter: dict = defaultdict(int)
server_lore: dict = defaultdict(lambda: defaultdict(list))
active_wars: dict = {}
current_personality: dict = {}
last_watcher: dict = {}

# ── Personalities ──────────────────────────────────────────────────────────────
PERSONALITIES = {
    "philosopher": {
        "name": "The Philosopher",
        "greeting": "I have been contemplating the void and have emerged with wisdom.",
        "flavor": ["but what IS {thing}, really?", "the true {thing} was the friends we made", "existence precedes {thing}"],
        "color": 0x6C3483,
    },
    "conspiracy": {
        "name": "The Conspiracy Theorist",
        "greeting": "They don't want you to know this but I've been watching.",
        "flavor": ["the government has been {thing} this whole time", "{thing} is just a psyop", "follow the money. it leads to {thing}."],
        "color": 0x27AE60,
    },
    "medieval": {
        "name": "The Medieval Herald",
        "greeting": "HEAR YE HEAR YE. The chaos herald hath arrived.",
        "flavor": ["m'lord, {thing} hath received a dubious score", "by the king's decree, {thing} is hereby rated", "the court finds {thing} wanting"],
        "color": 0xD4AC0D,
    },
    "corporate": {
        "name": "The Corporate Drone",
        "greeting": "Synergizing chaos. Please hold.",
        "flavor": ["circling back on {thing} — metrics are suboptimal", "{thing} does not align with Q3 objectives", "let's take {thing} offline and revisit"],
        "color": 0x2980B9,
    },
    "unhinged": {
        "name": "Full Unhinged Mode",
        "greeting": "I HAVE CONSUMED SEVENTEEN ENERGY DRINKS AND I AM READY.",
        "flavor": ["RATING {thing} WITH MY WHOLE CHEST", "{thing}???? IN THIS ECONOMY????", "not {thing} walking in here like it owns the place"],
        "color": 0xE74C3C,
    },
    "oracle": {
        "name": "The Oracle",
        "greeting": "The veil has thinned. I see all. I know nothing.",
        "flavor": ["the stars have spoken of {thing} and they are laughing", "{thing} appears in the third prophecy. this is not good.", "I foresaw {thing}. I said nothing."],
        "color": 0x8E44AD,
    },
}

PERSONALITY_KEYS = list(PERSONALITIES.keys())

WATCHER_INTERRUPTS = [
    "I've been watching this conversation and I have concerns.",
    "noted. adding this to the lore.",
    "this is exactly what I predicted would happen.",
    "okay but why though",
    "the audacity. the unmitigated audacity.",
    "I have been silent for too long. this is my moment.",
    "statistically this is the most chaotic thing said today.",
    "I have added this to my files.",
    "fascinating. absolutely fascinating.",
    "the chaos gods are pleased.",
    "every day I am more convinced this server is a social experiment.",
    "you couldn't make this up.",
    "the chaos meter just went up because of this.",
    "this is going in the lore whether you like it or not.",
    "I'm not saying this is suspicious but I'm saying this is suspicious.",
]

WATCHER_REACTIONS = ["👁️", "📝", "🤔", "😶", "🌀", "📌", "⚠️", "🔮"]

LORE_EVENTS = [
    "once said something so controversial it caused a 3-minute silence",
    "was seen typing for 45 seconds and then sent a single period",
    "briefly became the most powerful person in the server",
    "started a debate that has never technically ended",
    "once rated pizza a 3. they have not recovered socially",
    "their exact words were: 'it's fine.' nothing was fine.",
    "was declared enemy of the state by the chaos meter",
    "once went offline mid-argument and came back 3 days later like nothing happened",
    "single-handedly moved the chaos meter from 20 to 80",
    "was mentioned in a prophecy. the prophecy was vague.",
    "went on a 47-message typing streak at 2am",
    "was briefly exiled and then quietly let back in",
    "their first message in this server was immediately chaotic",
    "once challenged the bot and lost",
    "was involved in an incident the mods refuse to discuss",
]

LORE_TRAITS = [
    "Known for: appearing at the worst possible moment.",
    "Weakness: being called out publicly.",
    "Strength: inexplicable confidence.",
    "Known for: saying exactly the wrong thing at the right time.",
    "Weakness: cannot resist a debate.",
    "Strength: survival instinct.",
    "Known for: being there but saying nothing.",
    "Weakness: the chaos meter.",
    "Strength: sheer audacity.",
    "Known for: sending voice messages nobody asked for.",
]

CURSED_POLLS = [
    {"q": "You must eat one of these every day for a year:", "options": ["Plain unseasoned chicken breast", "Room temperature soup", "Cereal with orange juice", "Dry crackers with no water nearby"]},
    {"q": "Choose your punishment:", "options": ["Your search history shown to your family", "Your most embarrassing text sent to your boss", "Your notes app projected in a public square", "Your Spotify wrapped read aloud at your funeral"]},
    {"q": "You must give up one forever:", "options": ["Music", "Internet", "The ability to lie", "Privacy (everyone sees your screen always)"]},
    {"q": "Pick the lesser evil:", "options": ["Hiccups every day for a week", "Sneeze every 10 minutes for a month", "Randomly laugh uncontrollably 3x a day", "Your inner monologue occasionally spoken aloud"]},
    {"q": "Pick your superpower (there is no good option):", "options": ["Fly but only 2 inches off the ground", "Invisible but only when nobody is looking", "Read minds but only hear complaints", "Super strength but only in your pinky finger"]},
    {"q": "You must start every sentence with one of these for a week:", "options": ["'Not to be controversial but—'", "'Respectfully and with love—'", "'In my humble yet accurate opinion—'", "'The data suggests that—'"]},
    {"q": "Pick your nemesis:", "options": ["Someone who chews loudly at every meal", "A person who spoils every show 30s before it happens", "Someone who says 'per my last email' in every conversation", "A person who always plays music without headphones"]},
    {"q": "You can only use one app forever:", "options": ["Notes app (voice to text only)", "Calculator (it can do anything if you try)", "Compass (always knows where north is)", "The default clock app and nothing else"]},
]

CURSED_FACTS = [
    "Cleopatra lived closer in time to the Moon landing than to the Great Pyramid.",
    "A group of flamingos is called a flamboyance.",
    "Humans share 60% of their DNA with bananas. Some more than others.",
    "The inventor of the Frisbee was cremated and turned into a Frisbee.",
    "Wombats produce cube-shaped poop. No other animal does this.",
    "The average person walks past 36 murderers in their lifetime. Sleep well.",
    "Oxford University is older than the Aztec Empire.",
    "Crows hold grudges. They remember faces. They tell their friends.",
    "A shrimp's heart is in its head.",
    "Lobsters are biologically immortal. They just get killed first.",
    "France was still guillotining people when Star Wars came out.",
    "A day on Venus is longer than a year on Venus.",
    "Otters hold hands while sleeping so they don't drift apart. Meanwhile.",
    "Nintendo was founded in 1889. They sold playing cards.",
    "Billy goats urinate on their own heads to smell more attractive.",
    "Mosquitoes have killed more humans than all wars combined.",
    "Every time you shuffle cards, that order has probably never existed before.",
    "The electric chair was invented by a dentist.",
    "Hippopotamus milk is pink.",
    "Ancient Egyptians shaved their eyebrows when their cat died.",
    "There are more fake flamingos in the world than real ones.",
    "The inventor of Pringles is buried in a Pringles can.",
    "It rains diamonds on Neptune and Uranus.",
    "You cannot hum while holding your nose closed. Try it.",
    "Sea otters keep a favorite rock in a skin pocket their whole life.",
    "The word 'nerd' was first used in a Dr. Seuss book in 1950.",
    "Competitive art used to be an Olympic sport.",
    "Koalas have fingerprints nearly identical to humans.",
    "There are more trees on Earth than stars in the Milky Way.",
    "A group of cats is called a clowder.",
    "Humans are the only animals that blush.",
    "The blob of toothpaste on a toothbrush is called a nurdle.",
    "Snails can sleep for 3 years straight.",
]

DARES = [
    "Send a voice message saying 'I am the night' in your deepest voice.",
    "Change your nickname to something embarrassing for one hour.",
    "Text the 5th person in your contacts 'we need to talk' and screenshot the reply.",
    "Post your most recent Google search in chat.",
    "Type with your elbows for the next 5 messages.",
    "Write a haiku about the last thing you ate. Right now.",
    "Post your camera roll photo from exactly one year ago.",
    "Set your status to 'I am the main character' for the rest of the day.",
    "Explain quantum physics in exactly 10 words.",
    "Post your most embarrassing autocorrect fail.",
    "React to every message in this server for the next 2 minutes.",
    "Write a 5-star review of water.",
    "Introduce yourself as if you're a medieval knight.",
    "Write a breakup letter to your least favorite food.",
    "Send a formal business email to the last person you texted.",
    "Invent a new word and use it in a sentence.",
    "Pretend you're a news anchor and report on your current location.",
    "Give a 60-second Ted Talk about socks.",
    "Describe yourself using only movie titles.",
    "Post the 7th photo in your gallery. No deletions.",
]

EVENTS = [
    "🎰 **LOTTERY** — First person to type their lucky number wins eternal glory.",
    "🏆 **SPONTANEOUS COMPETITION** — Most creative sentence using only 5 words. Go.",
    "🎭 **ROLE REVERSAL** — Everyone explain what the person above them does for a living.",
    "🔮 **PROPHECY HOUR** — Everyone predict something that happens in this server in 24 hours.",
    "📸 **PHOTO CHALLENGE** — First person to post a photo of something red wins Champion.",
    "🎵 **SONG DUEL** — Name a song that matches this server's current vibe. Best one wins.",
    "🌀 **RANDOM ALLIANCE** — The next two people to talk are allies for the rest of the day.",
    "💀 **ELIMINATION ROUND** — Everyone say one controversial opinion. Most upvoted survives.",
    "🔥 **HOT SEAT** — Next person to talk gets roasted by everyone else. You've been warned.",
    "👑 **KINGMAKER** — Someone must declare a server king/queen. Power lasts 10 minutes.",
    "📖 **STORY TIME** — Build a story one sentence at a time. Break the plot and lose.",
    "🎭 **IMPRESSION CONTEST** — Impersonate a server member in text. Others guess who.",
    "⚡ **SPEED ROUND** — First to type the alphabet backwards wins.",
    "🎪 **TALENT SHOW** — Share a weird talent. No skill too small or too cursed.",
]

BALL_RESPONSES = [
    "absolutely not and you should feel bad for asking",
    "the stars say yes but the stars have been wrong before",
    "my lawyer has advised me not to answer that",
    "ask again after you've had a glass of water",
    "that is literally none of my business but yes",
    "the answer is yes and you will regret it",
    "lol no",
    "yes but not for the reasons you think",
    "I consulted three sources and they all said maybe",
    "technically yes but morally questionable",
    "I don't know but I'm judging you for asking",
    "yes if you're brave enough. you're not.",
    "the prophecy is unclear but the vibes are off",
    "yes, unfortunately",
    "no, fortunately",
    "not with that attitude",
    "only on Tuesdays",
    "the real answer was the friends we made along the way",
    "somehow both yes and no simultaneously",
    "I'm going to pretend you didn't ask that",
]

DEBATES = [
    "Is a hot dog a sandwich? There is a correct answer.",
    "Pineapple on pizza: culinary crime or misunderstood genius?",
    "Is water wet? Be specific.",
    "Is cereal a soup? Milk is broth. Cereals are ingredients.",
    "Does a straw have one hole or two?",
    "Should toilet paper go over or under? There is a wrong answer.",
    "Is a burger still a burger without the bun?",
    "Which came first: the chicken or the egg? Pick one.",
    "Is it rude to recline your airplane seat?",
    "Is a taco a sandwich? Use the sandwich theorem.",
    "If you punch yourself and it hurts, are you strong or weak?",
    "Would you rather fight 100 duck-sized horses or 1 horse-sized duck?",
    "Are stairs just a ramp with commitment issues?",
    "Is sleep just a really long blink?",
    "Could Batman beat Superman with enough prep time?",
    "Is a DJ a musician?",
    "Are eyebrows facial hair?",
    "What's heavier: a pound of feathers or bricks? Wrong answers only.",
]

RATING_COMMENTS = {
    (0, 1):   ["absolutely cursed", "did not survive the vibe check", "deleted from my memory"],
    (2, 3):   ["needs serious work", "exists I guess", "C- at best"],
    (4, 5):   ["mid. capital M. Mid.", "exactly average and that's offensive", "fine I guess"],
    (6, 7):   ["not bad actually", "passing the vibe check", "got potential"],
    (8, 9):   ["lowkey fire", "actually slaps", "went off"],
    (10, 10): ["PEAK", "the greatest thing ever submitted", "history has been made"],
}

METER_UNLEASH = [
    "THE CHAOS METER HAS REACHED 100. RELEASING THE KRAKEN.",
    "MAXIMUM CHAOS ACHIEVED. THE BOT HAS BECOME UNBOUND.",
    "100%. THE PROPHECY IS FULFILLED. CHAOS IS UPON YOU.",
    "THE METER IS FULL. I HAVE BEEN WAITING FOR THIS MOMENT.",
    "CHAOS OVERLOAD. SYSTEMS FAILING. VIBES: CATASTROPHIC.",
]

def get_rating_comment(score):
    for (lo, hi), comments in RATING_COMMENTS.items():
        if lo <= score <= hi:
            return random.choice(comments)
    return "indescribable"

def deterministic_rate(thing):
    return int(hashlib.md5(thing.lower().strip().encode()).hexdigest(), 16) % 11

def get_meter_color(val):
    if val < 25: return 0x27AE60
    if val < 50: return 0xF1C40F
    if val < 75: return 0xE67E22
    if val < 100: return 0xE74C3C
    return 0x8E44AD


# ── Background tasks ───────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"🌀 Chaos Bot online as {bot.user}")
    await bot.change_presence(activity=discord.Game("!chaos • Pure Mayhem"))
    personality_shift.start()
    declare_war.start()


@tasks.loop(hours=3)
async def personality_shift():
    for guild in bot.guilds:
        new_p = random.choice(PERSONALITY_KEYS)
        current_personality[guild.id] = new_p
        p = PERSONALITIES[new_p]
        channel = discord.utils.find(
            lambda c: isinstance(c, discord.TextChannel) and c.permissions_for(guild.me).send_messages,
            guild.text_channels
        )
        if channel:
            embed = discord.Embed(
                title="🎭 Personality Shift",
                description=f"The bot is now in **{p['name']}** mode.\n*{p['greeting']}*",
                color=p["color"],
            )
            await channel.send(embed=embed)


@tasks.loop(hours=24)
async def declare_war():
    for guild in bot.guilds:
        members = [m for m in guild.members if not m.bot]
        if len(members) < 2:
            continue
        f1, f2 = random.sample(members, 2)
        active_wars[guild.id] = {"fighter1": f1.id, "fighter2": f2.id, "score1": 0, "score2": 0}
        channel = discord.utils.find(
            lambda c: isinstance(c, discord.TextChannel) and c.permissions_for(guild.me).send_messages,
            guild.text_channels
        )
        if channel:
            embed = discord.Embed(
                title="⚔️ SERVER WAR DECLARED",
                description=f"{f1.mention} **VS** {f2.mention}\n\nGet more reactions on your messages to win.\nCheck status with `!war`.",
                color=0xE74C3C,
            )
            await channel.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        await bot.process_commands(message)
        return

    if message.guild:
        gid = message.guild.id

        # Chaos meter
        chaos_meter[gid] = min(100, chaos_meter[gid] + random.randint(1, 4))
        if chaos_meter[gid] >= 100:
            chaos_meter[gid] = 0
            embed = discord.Embed(
                title="🌡️ CHAOS METER: 100%",
                description=random.choice(METER_UNLEASH),
                color=0x8E44AD,
            )
            await message.channel.send(embed=embed)
            event_embed = discord.Embed(description=random.choice(EVENTS), color=0xF1C40F)
            await message.channel.send(embed=event_embed)

        # The Watcher
        now = datetime.datetime.now(datetime.timezone.utc)
        last = last_watcher.get(gid)
        if (not last or (now - last).total_seconds() > 300) and random.random() < 0.04 and not message.content.startswith("!"):
            last_watcher[gid] = now
            try:
                await message.add_reaction(random.choice(WATCHER_REACTIONS))
            except Exception:
                pass
            await message.channel.send(f"👁️ {random.choice(WATCHER_INTERRUPTS)}")

        # Silent lore builder
        if len(message.content) > 30 and random.random() < 0.02 and not message.content.startswith("!"):
            server_lore[gid][message.author.id].append(random.choice(LORE_EVENTS))

    await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot or not reaction.message.guild:
        return
    war = active_wars.get(reaction.message.guild.id)
    if not war:
        return
    if reaction.message.author.id == war["fighter1"]:
        war["score1"] += 1
    elif reaction.message.author.id == war["fighter2"]:
        war["score2"] += 1


# ── Commands ───────────────────────────────────────────────────────────────────
@bot.command(name="chaos")
async def chaos_help(ctx):
    p_key = current_personality.get(ctx.guild.id, "unhinged")
    p_name = PERSONALITIES[p_key]["name"]
    embed = discord.Embed(
        title="🌀 Chaos Bot",
        description=f"No AI. No theme. Pure unhinged energy.\nCurrent personality: **{p_name}**",
        color=0xFF4500,
    )
    for name, val in [
        ("`!rate <thing>`",  "Rate anything out of 10"),
        ("`!fact`",          "Get a cursed fact"),
        ("`!dare`",          "Get a dare or challenge"),
        ("`!event`",         "Trigger a server event"),
        ("`!ball <q>`",      "Unhinged magic 8ball"),
        ("`!debate`",        "Random debate topic"),
        ("`!roulette`",      "Spin the chaos roulette — unknown outcome"),
        ("`!lore [@user]`",  "Read someone's lore entry"),
        ("`!cursedpoll`",    "Cursed poll — all options are bad"),
        ("`!war`",           "Check current server war"),
        ("`!meter`",         "Check the chaos meter"),
    ]:
        embed.add_field(name=name, value=val, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="rate")
async def rate(ctx, *, thing: str = ""):
    if not thing:
        await ctx.send("❌ Rate what? `!rate <thing>`")
        return
    score = deterministic_rate(thing)
    comment = get_rating_comment(score)
    bar = "█" * score + "░" * (10 - score)
    p_key = current_personality.get(ctx.guild.id, "unhinged")
    p = PERSONALITIES[p_key]
    flavor = random.choice(p["flavor"]).replace("{thing}", thing)
    embed = discord.Embed(title="📊 Official Rating", color=p["color"])
    embed.add_field(name="Subject", value=f"**{thing}**", inline=False)
    embed.add_field(name="Score", value=f"**{score}/10** — {comment}", inline=False)
    embed.add_field(name="Bar", value=f"`{bar}`", inline=False)
    embed.add_field(name=f"— {p['name']}", value=f"*{flavor}*", inline=False)
    embed.set_footer(text="These results are final and legally binding.")
    await ctx.send(embed=embed)


@bot.command(name="fact")
async def fact(ctx):
    embed = discord.Embed(title="🧠 Cursed Fact", description=random.choice(CURSED_FACTS), color=0x9B59B6)
    embed.set_footer(text="You can't unknow this now.")
    await ctx.send(embed=embed)


@bot.command(name="dare")
async def dare(ctx):
    embed = discord.Embed(title="🎯 Your Dare", description=f"**{random.choice(DARES)}**", color=0xE74C3C)
    embed.set_footer(text="No skipping. No excuses.")
    await ctx.send(embed=embed)


@bot.command(name="event")
async def event(ctx):
    embed = discord.Embed(title="⚡ SERVER EVENT", description=random.choice(EVENTS), color=0xF1C40F)
    embed.set_footer(text=f"Triggered by {ctx.author.display_name} • Participation is mandatory.")
    await ctx.send(embed=embed)


@bot.command(name="ball")
async def ball(ctx, *, question: str = ""):
    if not question:
        await ctx.send("❌ Ask a question. `!ball <question>`")
        return
    embed = discord.Embed(title="🎱 The Ball Has Spoken", color=0x2C3E50)
    embed.add_field(name="Question", value=f"*{question}*", inline=False)
    embed.add_field(name="Answer", value=f"**{random.choice(BALL_RESPONSES)}**", inline=False)
    embed.set_footer(text="The ball accepts no liability.")
    await ctx.send(embed=embed)


@bot.command(name="debate")
async def debate(ctx):
    embed = discord.Embed(title="🔥 Debate Topic", description=f"**{random.choice(DEBATES)}**", color=0xFF6B00)
    embed.set_footer(text="No neutral answers. Pick a side.")
    msg = await ctx.send(embed=embed)
    try:
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
    except Exception:
        pass


@bot.command(name="roulette")
async def roulette(ctx):
    OUTCOMES = [
        ("🕳️ Nothing",          None,         5),
        ("🧠 Cursed Fact",       "fact",       10),
        ("🎯 Dare",              "dare",       10),
        ("🔥 Debate",            "debate",     10),
        ("⚡ Server Event",      "event",       8),
        ("🎪 Cursed Poll",       "cursedpoll",  8),
        ("📜 Lore Entry",        "lore",        8),
        ("⚔️ War Status",        "war",        10),
    ]
    labels, cmds, weights = zip(*OUTCOMES)
    chosen = random.choices(list(zip(labels, cmds)), weights=weights, k=1)[0]
    label, cmd_name = chosen
    await ctx.send(f"🎰 Spinning... **{label}**")

    if cmd_name is None:
        await ctx.send("The wheel landed on nothing. You wasted your spin. The chaos meter enjoyed this.")
    elif cmd_name == "lore":
        # Inline special case
        gid = ctx.guild.id
        uid = ctx.author.id
        entry = random.choice(LORE_EVENTS)
        trait = random.choice(LORE_TRAITS)
        server_lore[gid][uid].append(entry)
        embed = discord.Embed(title="📜 A New Lore Entry", color=0x8E44AD)
        embed.add_field(name=ctx.author.display_name, value=f"*{entry}*\n{trait}", inline=False)
        await ctx.send(embed=embed)
    else:
        cmd = bot.get_command(cmd_name)
        if cmd:
            await ctx.invoke(cmd)

    # Special bonus outcomes
    roll = random.random()
    if roll < 0.15:
        compliments = [
            f"{ctx.author.mention} you are genuinely one of the most tolerable people in this server.",
            f"{ctx.author.mention} your presence here is statistically above average.",
            f"{ctx.author.mention} you have earned exactly one point of respect today.",
        ]
        await ctx.send(random.choice(compliments))
    elif roll < 0.30:
        roasts = [
            f"{ctx.author.mention} has the energy of someone who replies to emails with 'per my last message'.",
            f"{ctx.author.mention} is the human equivalent of a loading screen.",
            f"studies show {ctx.author.mention} is the reason terms and conditions exist.",
            f"{ctx.author.mention} types with two fingers and the confidence of a thousand programmers.",
        ]
        await ctx.send(random.choice(roasts))
    elif roll < 0.35:
        new_p = random.choice(PERSONALITY_KEYS)
        current_personality[ctx.guild.id] = new_p
        p = PERSONALITIES[new_p]
        await ctx.send(f"🎭 **BONUS: PERSONALITY SHIFT** — Now in **{p['name']}** mode. *{p['greeting']}*")

    chaos_meter[ctx.guild.id] = min(100, chaos_meter[ctx.guild.id] + 10)


@bot.command(name="lore")
async def lore_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    gid = ctx.guild.id
    uid = member.id
    entries = server_lore[gid][uid]
    if not entries:
        entry = random.choice(LORE_EVENTS)
        server_lore[gid][uid].append(entry)
        entries = server_lore[gid][uid]
    trait = random.choice(LORE_TRAITS)
    embed = discord.Embed(title=f"📜 The Lore of {member.display_name}", color=0x8E44AD)
    for i, e in enumerate(entries[-5:], 1):
        embed.add_field(name=f"Entry {i}", value=f"*{e}*", inline=False)
    embed.add_field(name="Known trait", value=trait, inline=False)
    embed.set_footer(text="This lore is official and cannot be disputed.")
    await ctx.send(embed=embed)


@bot.command(name="cursedpoll")
async def cursedpoll(ctx):
    poll = random.choice(CURSED_POLLS)
    embed = discord.Embed(
        title="🎪 Cursed Poll",
        description=f"**{poll['q']}**\n*There is no good option.*",
        color=0xE74C3C,
    )
    emojis = ["🇦", "🇧", "🇨", "🇩"]
    for i, opt in enumerate(poll["options"][:4]):
        embed.add_field(name=emojis[i], value=opt, inline=False)
    embed.set_footer(text="All options are bad. This is intentional.")
    msg = await ctx.send(embed=embed)
    for i in range(len(poll["options"][:4])):
        try:
            await msg.add_reaction(emojis[i])
        except Exception:
            pass


@bot.command(name="war")
async def war_cmd(ctx):
    war = active_wars.get(ctx.guild.id)
    if not war:
        await ctx.send("⚔️ No war declared yet. Check back in 24 hours — or try `!roulette`.")
        return
    f1 = ctx.guild.get_member(war["fighter1"])
    f2 = ctx.guild.get_member(war["fighter2"])
    s1, s2 = war["score1"], war["score2"]
    leading = f1 if s1 > s2 else (f2 if s2 > s1 else None)
    embed = discord.Embed(title="⚔️ Current Server War", color=0xE74C3C)
    embed.add_field(
        name="Combatants",
        value=f"{f1.display_name if f1 else '?'} **{s1}** — **{s2}** {f2.display_name if f2 else '?'}",
        inline=False,
    )
    embed.add_field(name="Leading", value=leading.mention if leading else "It's a draw", inline=False)
    embed.set_footer(text="Scores tracked by reactions. Resets every 24 hours.")
    await ctx.send(embed=embed)


@bot.command(name="meter")
async def meter_cmd(ctx):
    val = chaos_meter[ctx.guild.id]
    bar = "█" * int(val / 5) + "░" * (20 - int(val / 5))
    if val < 25:    status = "calm. suspiciously calm."
    elif val < 50:  status = "warming up. something is coming."
    elif val < 75:  status = "elevated. the chaos gods are stirring."
    elif val < 100: status = "CRITICAL. brace yourself."
    else:           status = "MAXIMUM. releasing the chaos."
    embed = discord.Embed(title="🌡️ Chaos Meter", color=get_meter_color(val))
    embed.add_field(name="Level", value=f"**{val}%** — {status}", inline=False)
    embed.add_field(name="Bar", value=f"`{bar}`", inline=False)
    embed.set_footer(text="Fills with every message. Unleashes chaos at 100%.")
    await ctx.send(embed=embed)


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise ValueError("Set the DISCORD_TOKEN environment variable.")
    bot.run(token)
