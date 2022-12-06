# -*- coding: utf-8 -*-

from systems.imports import *

@dp.message_handler(lambda m: m.text.lower() in ["промокоды", "Промокоды"])
async def promiki(message):
	list = cursor.execute(f'SELECT * FROM promiki ORDER BY reward DESC').fetchmany(30)
	top_list = []
	rec = cursor.execute('SELECT * FROM promiki').fetchall()
	vsego2 = len(rec)
	if vsego2 == 0:
		return await message.answer('Промокодов еще не существует.')
	num = 0
	for user in list:
		num += 1
		top_list.append(f'{num}. {user[1]} | На одного: $<code>{user[2]}</code> | Активаций: {user[3]} | Активировало: {user[4]}')
	top = "\n".join(top_list)
	return await message.answer(f'Всего промокодов: {vsego2}\n\n' + top)

@dp.message_handler(lambda t: t.text.startswith("промо создать") or t.text.startswith("Промо создать") or t.text.startswith("создать промо") or t.text.startswith("Создать промо"))
async def promo(message):
	user_name = cursor.execute(f"SELECT user_name from users where user_id = {message.from_user.id}").fetchone()
	balance = cursor.execute(f"SELECT balance from users where user_id = {message.from_user.id}").fetchone()
	balance = round(int(balance[0]))
	balance2 = '{:,}'.format(balance).replace(',', '.')
	user_name = user_name[0]
	try:
		name = message.text.split()[2]
		akt = int(message.text.split()[3])
		dengi5 = message.text.split()[4]
	except:
		await message.answer(f'Использовать: промо создать [имя] [количество акт.] [сумма (на одного)]')
	cursor.execute(f"SELECT promo_name FROM promiki WHERE promo_name = '{name}' ") # тг превращает ' в "
	akt2 = '{:,}'.format(akt).replace(',', '.')
	dengi4 = (dengi5).replace(' ', '').replace('k', '000').replace('е','e').replace('к', '000').replace(',', '').replace('.', '').replace("$", "").replace('м', '000000').replace('m', '000000')
	dengi3 = float(dengi4)
	dengi = int(dengi3)
	denfi = int(dengi*akt)
	denfi2 = '{:,}'.format(denfi).replace(',', '.')
	dengi2 = '{:,}'.format(dengi).replace(',', '.')
	if cursor.fetchone() != None:
		return await message.answer(f'Имя промокода "{name}" занято.')
	if dengi*akt > balance:
		return await message.answer(f'❗Не достаточно средств для создания промокода!\n📑 Нужно: <code>{denfi2}</code>\n📄 На балансе: <code>{balance2}</code>')
	if len(name) < 3 or len(name) > 24:
		return await message.answer(f'❕Вы не можете создать промокод с названием меньше 3 символов и больше 24 символов.')
	if akt < 2:
		return await message.answer(f'❌ Извини, но нельзя создавать промокоды, где кодичество активаций 1')
	if dengi < 100:
		return await message.answer(f'❌ Извини, но нельзя создавать промокоды, где на одного пользователя дают: <code>100</code>$')
	cursor.execute(f"INSERT INTO promiki VALUES ({message.from_user.id}, '{name}', {dengi}, {akt}, 0)")
	connect.commit()
	cursor.execute(f'UPDATE users SET balance = {balance-dengi*akt} WHERE user_id = {message.from_user.id}')
	connect.commit()
	return await message.answer(f'✔️ Вы успешно создали промокод: «<code>{name}</code>»\n✅ Количество активаций: <code>{akt2}</code>\n👥 На одного пользователя: <code>{dengi2}</code>$\n🧾 С баланса было снято: <code>{denfi2}</code>$')
	
@dp.message_handler(lambda t: t.text.startswith("промо") or t.text.startswith("Промо"))
async def promoco(message):
	try:
		vvod = message.text.split()[1]
	except:
		return await message.answer(f'❌ Вы не ввели имя промокода')
	cursor.execute(f"SELECT activation FROM promo WHERE user_id = {message.from_user.id} AND promo_name = '{vvod}'")
	if cursor.fetchone() != None:
		return await message.answer(f'❌ Вы уже активировали данный промокод')
	cursor.execute(f"SELECT promo_name FROM promiki WHERE promo_name = '{vvod}'")
	if cursor.fetchone() == None:
		return await message.answer('Данного промокода не существует.')
	cursor.execute(f"SELECT users, max_users, reward FROM promiki WHERE promo_name = '{vvod}'")
	for k in cursor.fetchall():
		if k[0] >= k[1]:
			pp = '{:,}'.format(k[1]).replace(',', '.')
			return await message.answer(f'👥 Этот промокод уже активировало все <code>{pp}</code> пользователей.', parse_mode='html')
	cursor.execute(f"UPDATE promiki SET users = users + 1 WHERE promo_name = '{vvod}'")
	cursor.execute(f"UPDATE users SET balance = balance + {k[2]} WHERE user_id = {message.from_user.id}")
	cursor.execute(f"INSERT INTO promo VALUES ({message.from_user.id}, 1, '{vvod}')")
	connect.commit()
	money = '{:,}'.format(k[2]).replace(',', '.')
	balance = cursor.execute("SELECT balance from users where user_id = ?", (message.from_user.id,)).fetchone()
	balance = round(int(balance[0]))
	balik2 = '{:,}'.format(balance).replace(',', '.')
	return await message.answer(f'👤 Вы активировали промокод\n✅ На ваш баланс зачислено: <code>{money}</code>$\nТеперь ваш баланс составляет: <code>{balik2}</code>$', parse_mode='html')