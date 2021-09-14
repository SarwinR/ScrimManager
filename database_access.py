import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import discord
from discord.ext import commands

import os
import base64
import json

db = None

#link to the main database
def initialize_database():
    db_key_str= base64.b64decode(os.getenv('DB_KEY'))
    db_key_json = json.loads(db_key_str)

    # Use a service account
    cred = credentials.Certificate(db_key_json)
    firebase_admin.initialize_app(cred)

    global db
    db = firestore.client()


async def load_user_profile(id:int, request:str="wins"):
    global db

    profile_ref = db.collection(str(id)).document(request)
    profile = profile_ref.get()

    if profile.exists:
        data = profile.to_dict()
    else:
        data = await initialize_user_profile(id, request)

    return data


async def update_user_profile(id:int, data:dict, request:str="wins"):
    global db

    profile_ref = db.collection(str(id)).document(request)

    profile_ref.update(data)


async def initialize_user_profile(id:int, request:str):
    global db

    profile_ref = db.collection(str(id)).document(request)

    if(request == 'wins'):
        profile_ref.set({
         u's': 0,
         u'd': 0,
         u't': 0,
         u'tournament':0
        })

    profile_ref = db.collection(str(id)).document(request)
    profile = profile_ref.get()

    return profile.to_dict()


async def cache_data(mode, data):
    global db

    profile_ref = db.collection('cache').document(mode)

    profile_ref.update(data)


async def load_leaderboard(self, ctx, mode):
    global db

    raw_data = db.collection("cache").document(mode)
    data = raw_data.get()
    dict_data = data.to_dict()

    ordered_data = sorted(dict_data, key=dict_data.get)

    top_10_data = list(ordered_data)
    real = top_10_data.reverse()
    print(top_10_data)
    #print(real)

    '''
	index = len(real) - 1

	for i in range(len(real)):
		top_10_data[i] = real[index - i]
	'''

    list_gamemode = ['SOLO', 'DUO', 'TRIO', 'TOURNAMENT']
    game_mode_display = list_gamemode[['s', 'd', 't', 'tournament'].index(mode)]

    leaderboard_embed=discord.Embed(title="{} LEADERBOARD".format(game_mode_display),color=0xe100ff)
    for d in top_10_data:
        user = await self.client.fetch_user(int(d))
        print("{} - {}".format(user.name, dict_data[d]))
    #leaderboard_embed.add_field(name=user.name ,value=dict_data[d], inline=False)

    print("done")

    leaderboard_embed.set_footer(text="If you are not on the leaderboard\n despite having enough wins, do \n[.profile] to cache your data")
    await ctx.reply(embed=leaderboard_embed)
