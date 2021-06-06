import aiohttp
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import json
import typing as tp

bot = Bot(token='1383237591:AAENpQQX190rqqI1CnCMK0Hu3vcIgBEkNUE')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message) -> None:
    await message.reply("Hi!\nI'm CinemaBot!\nPowered by aiogram.")


@dp.message_handler(commands=['help'])
async def help(message: types.Message) -> None:
    await message.reply("how can i help")


def get_films(data: tp.Dict[tp.Any, tp.Any]) -> tp.List[tp.Dict[tp.Any, tp.Any]]:
    ans: tp.Dict[tp.Any, tp.Any] = {}

    for film in data['films']:
        if 'rating' not in film.keys():
            continue
        try:
            float(film['rating'])
        except:
            continue

        if not ans:
            ans = film
        elif ans['rating'] < film['rating']:
            ans = film

    result: tp.List[tp.Dict[tp.Any, tp.Any]] = []
    result.append(ans)
    film_ids: tp.List[int] = []
    film_ids.append(ans['filmId'])

    for film in data['films']:
        if 'rating' not in film.keys():
            continue
        try:
            float(film['rating'])
        except:
            continue

        if float(ans['rating']) - float(film['rating']) < 1.5 and film['filmId'] not in film_ids:
            result.append(film)
            film_ids.append(film['filmId'])
    return result


def get_messsage_by_film(ans: tp.Dict[tp.Any, tp.Any]) -> str:
    text = ''
    text += 'Название: ' + ans['nameRu'] + '\n'
    text += 'Год выпуска: ' + ans['year'] + '\n'
    text += 'Рейтинг: ' + ans['rating'] + '\n'
    text += 'Жанр: '
    for genre in ans['genres']:
        text += genre['genre'] + ' '
    text += '\n'
    text += 'Описание\n' + ans['description'] + '\n'
    text += 'Глянуть можно тут: ' + 'http://www.kinopoisk.ru/film/' + str(ans['filmId']) + '/'

    return text


@dp.message_handler()
async def echo(message: types.Message) -> None:
    name = message.text
    async with aiohttp.ClientSession(headers={'X-API-KEY': 'ce0aba2a-6b03-4f23-9619-af26e384edab'}) as session:
        async with session.get('https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword',
                               params={'keyword': name}) as resp:
            text = await resp.text()
            status = resp.status
    if status != 200:
        await message.answer('Ничего не нашел(((')
        return

    data = json.loads(text)
    ans = get_films(data)
    ans = sorted(ans, key=lambda item: item['year'])

    if not ans:
        await message.answer('Ничего не нашел(((')
        return

    await message.reply("Вот что я нашел!")

    for film in ans:
        await message.reply(get_messsage_by_film(film))


if __name__ == '__main__':
    executor.start_polling(dp)
