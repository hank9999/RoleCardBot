# -*- encoding : utf-8 -*-
import json
import math
import os
from khl import Bot, Message, Cert, EventTypes, Event, HTTPRequester, Gateway
from khl.card import Card, Types, Module, CardMessage, Element
from khl.command import Rule

# webhook
# bot = Bot(cert=Cert(token='token', verify_token='verify_token'), port=3000,
#           route='/khl-wh')

# websocket
bot = Bot(token='token')


# 0->操作成功 1->角色卡已存在
async def create_card(guild: str, card_name: str) -> int:
    cards_file = f'cards/{guild}.json'
    if not os.path.exists(cards_file):
        with open(cards_file, 'w') as f:
            f.write(json.dumps({card_name: []}))
        return 0
    else:
        with open(cards_file, 'r') as f:
            cards = json.loads(f.read())
        if card_name in cards:
            return 1
        cards[card_name] = []
        with open(cards_file, 'w') as f:
            f.write(json.dumps(cards))
        return 0


# 0->操作成功 2->角色卡不存在
async def del_card(guild: str, card_name: str) -> int:
    cards_file = f'cards/{guild}.json'
    if not os.path.exists(cards_file):
        return 2
    else:
        with open(cards_file, 'r') as f:
            cards = json.loads(f.read())
        if card_name not in cards:
            return 2
        del cards[card_name]
        with open(cards_file, 'w') as f:
            f.write(json.dumps(cards))
        return 0


# 2->角色卡不存在
async def list_card(guild: str):
    cards_file = f'cards/{guild}.json'
    if not os.path.exists(cards_file):
        return 2
    else:
        with open(cards_file, 'r') as f:
            cards = json.loads(f.read())
        return cards.keys()


# 0->操作成功 2->角色卡不存在
async def add_role(guild: str, card_name: str, role: list) -> int:
    cards_file = f'cards/{guild}.json'
    if not os.path.exists(cards_file):
        return 2
    else:
        with open(cards_file, 'r') as f:
            cards = json.loads(f.read())
        if card_name not in cards:
            return 2
        for i in role:
            if i not in cards[card_name]:
                cards[card_name].append(i)
        with open(cards_file, 'w') as f:
            f.write(json.dumps(cards))
        return 0


# 0->操作成功 2->角色卡不存在 3->角色不存在
async def del_role(guild: str, card_name: str, role: str) -> int:
    cards_file = f'cards/{guild}.json'
    if not os.path.exists(cards_file):
        return 2
    else:
        with open(cards_file, 'r') as f:
            cards = json.loads(f.read())
        if card_name not in cards:
            return 2
        if role not in cards[card_name]:
            return 3
        cards[card_name].remove(role)
        with open(cards_file, 'w') as f:
            f.write(json.dumps(cards))
        return 0


# 2->角色卡不存在
async def list_role(guild: str, card_name: str):
    cards_file = f'cards/{guild}.json'
    if not os.path.exists(cards_file):
        return 2
    else:
        with open(cards_file, 'r') as f:
            cards = json.loads(f.read())
        if card_name not in cards:
            return 2
        return cards[card_name]


async def get_master_id(guild: str):
    result = await bot.client.gate.request('GET', 'guild/view', params={'guild_id': guild})
    return result['master_id']


# 0->操作成功
async def add_permission(guild: str, users: list):
    permission_file = f'permissions/{guild}.json'
    if not os.path.exists(permission_file):
        with open(permission_file, 'w') as f:
            f.write(json.dumps(users))
        return 0
    else:
        with open(permission_file, 'r') as f:
            permission = json.loads(f.read())
        for i in users:
            if i not in permission:
                permission.append(i)
        with open(permission_file, 'w') as f:
            f.write(json.dumps(permission))
        return 0


# 0->操作成功 4-> 权限不存在
async def del_permission(guild: str, user_id: str):
    permission_file = f'permissions/{guild}.json'
    if not os.path.exists(permission_file):
        return 4
    else:
        with open(permission_file, 'r') as f:
            permission = json.loads(f.read())
        if user_id not in permission:
            return 4
        permission.remove(user_id)
        with open(permission_file, 'w') as f:
            f.write(json.dumps(permission))
        return 0


# 0->操作成功 4-> 权限不存在
async def list_permission(guild: str):
    permission_file = f'permissions/{guild}.json'
    if not os.path.exists(permission_file):
        return 4
    else:
        with open(permission_file, 'r') as f:
            permission = json.loads(f.read())
        return permission


async def check_permission(guild: str, user_id: str) -> bool:
    result = False
    permission = await list_permission(guild)
    if permission != 4 and (user_id in permission):
        result = True
    if not result:
        master_id = await get_master_id(guild)
        if master_id == user_id:
            result = True
    return result


async def get_user(user_id: str):
    result = await bot.client.gate.request('GET', 'user/view', params={'user_id': user_id})
    return result


async def get_all_role_names(msg: Message):
    role_parts = (await msg.gate.request('GET', 'guild-role/list', params={'guild_id': msg.ctx.guild.id}))['items']
    role_parts_names = {}
    for i in role_parts:
        role_parts_names[str(i['role_id'])] = i['name']
    return role_parts_names


async def card_generate(card_name: str, roles: list) -> Card:
    c = Card()
    c.append(Module.Header(f'{card_name}'))
    c.append(Module.Divider())
    for i in roles:
        if len(i) == 3:
            m = Module.ActionGroup(
                Element.Button(i[0]['name'],
                               '{"operate": "get_role", "role_id": ' + i[0]['role_id'] + ', "name": "' + i[0][
                                   'name'] + '"}', Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
                Element.Button(i[1]['name'],
                               '{"operate": "get_role", "role_id": ' + i[1]['role_id'] + ', "name": "' + i[1][
                                   'name'] + '"}', Types.Click.RETURN_VAL, theme=Types.Theme.SUCCESS),
                Element.Button(i[2]['name'],
                               '{"operate": "get_role", "role_id": ' + i[2]['role_id'] + ', "name": "' + i[2][
                                   'name'] + '"}', Types.Click.RETURN_VAL, theme=Types.Theme.INFO)
            )
            c.append(m)
            c.append(Module.Divider())
        elif len(i) == 2:
            m = Module.ActionGroup(
                Element.Button(i[0]['name'],
                               '{"operate": "get_role", "role_id": ' + i[0]['role_id'] + ', "name": "' + i[0][
                                   'name'] + '"}', Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
                Element.Button(i[1]['name'],
                               '{"operate": "get_role", "role_id": ' + i[1]['role_id'] + ', "name": "' + i[1][
                                   'name'] + '"}', Types.Click.RETURN_VAL, theme=Types.Theme.SUCCESS)
            )
            c.append(m)
        elif len(i) == 1:
            m = Module.ActionGroup(
                Element.Button(i[0]['name'],
                               '{"operate": "get_role", "role_id": ' + i[0]['role_id'] + ', "name": "' + i[0][
                                   'name'] + '"}', Types.Click.RETURN_VAL, theme=Types.Theme.DANGER)
            )
            c.append(m)
    return c


async def split_every_four_roles(all_roles: dict):
    count = math.ceil(len(all_roles) / 3.0)
    split_roles = [[] for _ in range(0, count)]
    now_index = 0
    for k, v in all_roles.items():
        if len(split_roles[now_index]) == 3:
            now_index += 1
        split_roles[now_index].append({'role_id': k, 'name': v})
    return split_roles


@bot.command(name='角色卡创建', prefixes=['.', '。', '/'])
async def role_card_add(msg: Message, card_name: str = ''):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    if card_name == '':
        await msg.reply('角色卡名称不能为空')
        return
    result = await create_card(msg.ctx.guild.id, card_name)
    if result == 0:
        await msg.reply(f'角色卡 {card_name} 创建成功')
    elif result == 1:
        await msg.reply(f'角色卡 {card_name} 已存在')


@bot.command(name='角色卡删除', prefixes=['.', '。', '/'])
async def role_card_del(msg: Message, card_name: str = ''):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    if card_name == '':
        await msg.reply('角色卡名称不能为空')
        return
    result = await del_card(msg.ctx.guild.id, card_name)
    if result == 0:
        await msg.reply(f'角色卡 {card_name} 删除成功')
    elif result == 2:
        await msg.reply(f'角色卡 {card_name} 不存在')


@bot.command(name='角色卡列表', prefixes=['.', '。', '/'])
async def role_card_list(msg: Message, *args):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    result = await list_card(msg.ctx.guild.id)
    if result == 2:
        await msg.reply(f'不存在角色卡')
    elif len(result) == 0:
        await msg.reply(f'不存在角色卡')
    else:
        cards_name_list = ''
        for i in result:
            cards_name_list += f'    {i}\n'
        await msg.reply(f'角色卡列表:\n{cards_name_list}')


@bot.command(name='角色卡生成', prefixes=['.', '。', '/'])
async def role_card_create(msg: Message, card_name: str = ''):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    if card_name == '':
        await msg.reply('角色卡名称不能为空')
        return
    result = await list_role(msg.ctx.guild.id, card_name)
    if result == 2:
        await msg.reply(f'角色卡 {card_name} 不存在')
    elif len(result) == 0:
        await msg.reply(f'角色卡 {card_name} 中不存在角色')
    else:
        all_role_names = await get_all_role_names(msg)
        role_names = {}
        for i in result:
            if i not in all_role_names:
                role_names[i] = '角色不存在'
            else:
                role_names[i] = all_role_names[i]
        roles_every_four = await split_every_four_roles(role_names)
        c = await card_generate(card_name, roles_every_four)
        await msg.ctx.channel.send(CardMessage(c))


@bot.command(regex=r'(?:.+|)(?:\.|\/|。)(?:角色卡更新)(.+|)')
async def role_card_update(msg: Message, card_name: str = ''):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    card_name = card_name.strip()
    if 'quote' not in msg.extra:
        await msg.reply('请引用源消息')
        return
    if card_name == '':
        await msg.reply('角色卡名称不能为空')
        return
    result = await list_role(msg.ctx.guild.id, card_name)
    if result == 2:
        await msg.reply(f'角色卡 {card_name} 不存在')
    elif len(result) == 0:
        await msg.reply(f'角色卡 {card_name} 中不存在角色')
    else:
        all_role_names = await get_all_role_names(msg)
        role_names = {}
        for i in result:
            if i not in all_role_names:
                role_names[i] = '角色不存在'
            else:
                role_names[i] = all_role_names[i]
        roles_every_four = await split_every_four_roles(role_names)
        c = await card_generate(card_name, roles_every_four)
        msg_id = msg.extra['quote']['rong_id']
        await msg.gate.request('POST', 'message/update', data={'msg_id': msg_id, 'content': json.dumps(CardMessage(c))})


@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def btn_value(_: Bot, e: Event):
    if e.body['channel_type'] != 'GROUP':
        return
    return_val = json.loads(e.body['value'])
    operate = return_val['operate']
    if operate == 'get_role':
        role_id = return_val['role_id']
        name = return_val['name']
        guild_id = e.body['guild_id']
        user_id = e.body['user_info']['id']
        channel_id = e.body['target_id']
        try:
            await bot.client.gate.request('POST', 'guild-role/grant',
                                          data={'guild_id': guild_id, 'user_id': user_id, 'role_id': role_id})
            ch = await bot.fetch_public_channel(channel_id)
            await ch.send(f'角色 {name} 添加成功', temp_target_id=user_id)
        except HTTPRequester.APIRequestFailed as ex:
            ch = await bot.fetch_public_channel(channel_id)
            await ch.send(f'角色 {name} 添加失败 {ex.err_message}', temp_target_id=user_id)


@bot.command(name='角色添加', prefixes=['.', '。', '/'])
async def role_add(msg: Message, card_name: str = '', *args):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    if card_name == '':
        await msg.reply('角色卡名称不能为空')
        return
    mention_roles = msg.extra['mention_roles']
    if len(mention_roles) == 0:
        await msg.reply('请at角色')
        return
    roles = []
    roles_name = ''
    for i in mention_roles:
        roles.append(str(i))
    for i in msg.extra['kmarkdown']['mention_role_part']:
        roles_name += f"{i['name']}#{i['role_id']}, "
    roles_name = roles_name[:-2]
    result = await add_role(msg.ctx.guild.id, card_name, roles)
    if result == 0:
        await msg.reply(f'角色卡 {card_name} 中角色 {roles_name} 添加成功')
    elif result == 2:
        await msg.reply(f'角色卡 {card_name} 不存在')


@bot.command(name='角色删除', prefixes=['.', '。', '/'])
async def role_del(msg: Message, card_name: str = '', *args):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    if card_name == '':
        await msg.reply('角色卡名称不能为空')
        return
    mention_roles = msg.extra['mention_roles']
    if len(mention_roles) == 0:
        await msg.reply('请at角色')
        return
    if len(mention_roles) > 1:
        await msg.reply(f'一次只能删除一个角色卡角色')
        return
    role = str(mention_roles[0])
    role_name = msg.extra['kmarkdown']['mention_role_part'][0]['name']
    result = await del_role(msg.ctx.guild.id, card_name, role)
    if result == 0:
        await msg.reply(f'角色卡 {card_name} 中角色 {role_name} 删除成功')
    elif result == 2:
        await msg.reply(f'角色卡 {card_name} 不存在')
    elif result == 3:
        await msg.reply(f'角色卡 {card_name} 中不存在角色 {role_name}')


@bot.command(name='角色列表', prefixes=['.', '。', '/'])
async def role_list(msg: Message, card_name: str = ''):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    if card_name == '':
        await msg.reply('角色卡名称不能为空')
        return
    result = await list_role(msg.ctx.guild.id, card_name)
    if result == 2:
        await msg.reply(f'角色卡 {card_name} 不存在')
    elif len(result) == 0:
        await msg.reply(f'角色卡 {card_name} 中不存在角色')
    else:
        all_role_names = await get_all_role_names(msg)
        role_names_list = ''
        for i in result:
            if i not in all_role_names:
                role_names_list += f'    角色不存在#{i}\n'
            else:
                role_names_list += f"    {all_role_names[i]}#{i}\n"
        await msg.reply(f'角色卡 {card_name} 中角色:\n{role_names_list}')


@bot.command(name='清除失效角色', prefixes=['.', '。', '/'])
async def invalid_role_clean(msg: Message, card_name: str = ''):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    if card_name == '':
        await msg.reply('角色卡名称不能为空')
        return
    result = await list_role(msg.ctx.guild.id, card_name)
    if result == 2:
        await msg.reply(f'角色卡 {card_name} 不存在')
    elif len(result) == 0:
        await msg.reply(f'角色卡 {card_name} 中不存在角色')
    else:
        all_role_names = await get_all_role_names(msg)
        invalid_roles = ''
        for i in result:
            if i not in all_role_names:
                invalid_roles += f'{i}, '
                await del_role(msg.ctx.guild.id, card_name, i)
        invalid_roles = invalid_roles[:-2]
        await msg.reply(f'角色卡 {card_name} 中失效角色 {invalid_roles} 已清除')


@bot.command(name='权限添加', prefixes=['.', '。', '/'])
async def permission_add(msg: Message, *args):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    mention = msg.extra['mention']
    if len(mention) == 0:
        await msg.reply('请at用户')
        return
    users_name = ''
    for i in msg.extra['kmarkdown']['mention_part']:
        users_name += f"{i['full_name']}, "
    users_name = users_name[:-2]
    result = await add_permission(msg.ctx.guild.id, mention)
    if result == 0:
        await msg.reply(f'权限添加 {users_name} 成功')


@bot.command(name='权限删除', prefixes=['.', '。', '/'])
async def permission_add(msg: Message, *args):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    mention = msg.extra['mention']
    if len(mention) == 0:
        await msg.reply('请at用户')
        return
    if len(mention) > 1:
        await msg.reply(f'一次只能删除一个权限')
        return
    users_name = msg.extra['kmarkdown']['mention_part'][0]['full_name']
    result = await del_permission(msg.ctx.guild.id, mention[0])
    if result == 0:
        await msg.reply(f'权限删除 {users_name} 成功')
    elif result == 4:
        await msg.reply(f'权限不存在')


@bot.command(name='权限列表', prefixes=['.', '。', '/'])
async def permission_list(msg: Message, *args):
    if not (await check_permission(msg.ctx.guild.id, msg.author_id)):
        await msg.reply('您没有权限执行此操作')
        return
    result = await list_permission(msg.ctx.guild.id)
    if result == 4:
        await msg.reply(f'权限列表为空')
    elif len(result) == 0:
        await msg.reply(f'权限列表为空')
    else:
        users_name = ''
        for i in result:
            user = await get_user(i)
            users_name += f"    {user['username']}#{user['identify_num']}\n"
        await msg.reply(f'权限列表: \n{users_name}')


@bot.command(name='帮助', rules=[Rule.is_bot_mentioned(bot)], prefixes=['.', '。', '/'])
async def bot_help(msg: Message, *args):
    text1 = """
请在指令前添加前缀 . | 。 | / 三者任意一种
下面为指令列表, 所有指令与参数之间均存在 **空格**
---
角色卡创建 `角色卡名称`
  - 创建一个名为 `角色卡名称` 的角色卡
  - 角色卡名称为自定义内容
  - 如果中间存在空格或者符号`'` 请将整个名称用英文双引号包裹 下同
---
角色卡删除 `角色卡名称`
  - 删除一个名为 `角色卡名称` 的角色卡
---
角色卡列表
  - 显示所有存在的角色卡
---
角色卡生成 `角色卡名称`
  - 生成名为 `角色卡名称` 的角色卡
---
角色卡更新 `角色卡名称`
  - 更新名为 `角色卡名称` 的角色卡
  - 此功能需要你引用/回复已经生成的角色卡消息
---
角色添加 `角色卡名称` `@需要添加的身份组`
  - 该指令可一次性添加多个身份组到名为 `角色卡名称` 的角色卡中
---
角色删除 `角色卡名称` `@需要删除的身份组`
  - 该指令一次性只能删除名为 `角色卡名称` 的角色卡中的一个身份组
---
角色列表 `角色卡名称`
  - 显示该角色卡中所有的身份组
---
清除失效角色 `角色卡名称`
  - 清理已删除却仍保存在名为 `角色卡名称` 角色卡中的身份组
---
权限添加 `@需要添加权限的用户`
  - 该指令可一次性添加多个用户的权限
---
权限删除 `@需要删除权限的用户`
  - 该指令一次性只能一个用户的权限
---
权限列表
  - 显示所有拥有管理角色卡权限的用户 (服主默认拥有权限)
"""
    text2 = """
第一次使用: 角色卡创建 -> 角色添加 -> 角色卡生成
角色卡更新: 角色添加/删除(或者清除失效角色) -> 角色卡更新
管理其他用户管理角色卡的权限: 权限添加 | 权限删除
"""
    c1 = Card()
    c1.append(Module.Header('角色卡机器人帮助'))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text(text1[1:-1], type=Types.Text.KMD)))
    c2 = Card()
    c2.theme = Types.Theme.WARNING
    c2.append(Module.Header('角色卡机器人使用流程'))
    c2.append(Module.Divider())
    c2.append(Module.Section(Element.Text(text2[1:-1], type=Types.Text.KMD)))
    await msg.reply(CardMessage(c1, c2))


if __name__ == '__main__':
    bot.run()
