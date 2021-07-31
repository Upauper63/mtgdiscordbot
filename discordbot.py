import discord
from pymongo import MongoClient
import os
TOKEN = os.environ.get('TOKEN')
DBUSER = os.environ.get('DBUSER')

# mongodb設定
db_name = 'mtgcards'
client = MongoClient("mongodb://" + DBUSER + "@mtgcardscluster0-shard-00-00.ingul.mongodb.net:27017,mtgcardscluster0-shard-00-01.ingul.mongodb.net:27017,mtgcardscluster0-shard-00-02.ingul.mongodb.net:27017/" + db_name + "?ssl=true&replicaSet=atlas-efqnvm-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.mtgcards
collec = db.mtgcards


client = discord.Client()
@client.event
async def on_ready():
    print('BotScript起動')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith('?') or message.content.startswith('？'):
        # 全角半角対応
        input_words = message.content.replace('？', '?')
        input_words = str.lower(input_words[1:])
        # 完全一致
        card = collec.find_one({'name': input_words})
        if not card:
            # 全角対応して複数キーワードをリスト化
            input_words = input_words.replace('　', ' ').split(' ')
            search_words = []
            for input_word in input_words:
                search_words.append({"name": {"$regex": input_word}})
            # search_words = search_words[:-1]
            if not search_words:
                await message.channel.send('カード名が間違っている可能性があります。')
                return
            # 複数キーワードをand条件でフィルター
            pipeline = [{"$match": {"$and": search_words}}]
            # indexエラーなどでexcept
            try:
                card = list(collec.aggregate(pipeline))[0]
            except:
                await message.channel.send('カード名が間違っている可能性があります。')
                return
        link = card['link']
        try:
            url = 'https://drive.google.com/uc?export=download&id=' + link
            await message.channel.send(url)
        except:
            await message.channel.send('送信エラー')
        return
client.run(TOKEN)