from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_admin_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Объявить игру", callback_data='game_announcement')],
        [InlineKeyboardButton(text='Опросы о видео', callback_data='poll_announcement')],
        [InlineKeyboardButton(text='Сообщение в Анонсы', callback_data='message_announcement')]
    ])

game_announcement_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Дата', callback_data='game_announcement:date'),
         InlineKeyboardButton(text='Время', callback_data='game_announcement:time'),
         InlineKeyboardButton(text='Название', callback_data='game_announcement:name'),
         InlineKeyboardButton(text='Место', callback_data='game_announcement:location'),
         InlineKeyboardButton(text='Картинка', callback_data='game_announcement:picture'),
         InlineKeyboardButton(text='Отправить', callback_data='game_announcement:send')],
    ])

poll_admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить видео', callback_data='poll_announcement:add_video')],
    [InlineKeyboardButton(text='Удалить видео', callback_data='poll_announcement:delete_video')],
    [InlineKeyboardButton(text='Отправить опрос', callback_data='poll_announcement:send')],
])