from PIL import Image,ImageDraw
import PIL
import configparser
import logging

import telegram
from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters
from    telegram.ext import Updater,CommandHandler   ,InlineQueryHandler,ChosenInlineResultHandler,CallbackQueryHandler

from telegram import InlineQueryResultArticle,InputTextMessageContent,InlineKeyboardButton,InlineKeyboardMarkup
import requests
import time
	
import random
# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=(config['TELEGRAM']['ACCESS_TOKEN']))
def bit(x):
	cnt=0
	while x>0:
		x//=2
		cnt+=1
	return cnt


class game():
	def __init__(self):
		self.map = [[0 for i in range(15)] for j in range(15)]
		self.tm_cnt = 'A'
		for i in range(0,15):
			for j in range(0,15):
				self.map[i][j] = 'N'
	def draw(self):
		image = Image.new('RGBA',(300,300))
		draw = ImageDraw.Draw(image)
		draw.rectangle((0,0,299,299),fill = (255,255,255,255),outline = (255,255,255,255))
		for i in range(20,320,20):
			if i % 100 != 0:	
				draw.line((0,i,299,i),fill = (0,0,0,255))
				draw.line((i,0,i,299),fill = (0,0,0,255))
			else:
				draw.line((0,i,299,i),fill = (0,0,0,255),width=4)
				draw.line((i,0,i,299),fill = (0,0,0,255),width=4)
		
		for y in range(0,15): 
			for x in range(0,15): 
				if self.map[y][x] == 'A':
					draw.ellipse((x*20+4,y*20+4,x*20+16,y*20+16),fill =(0,0,0,0),outline=(0,0,0,255)) 
				if self.map[y][x] == 'B':
					draw.line((x*20+4,y*20+4,x*20+16,y*20+16),fill = (0,0,0,255),width=2)
					draw.line((x*20+16,y*20+5,x*20+4,y*20+14),fill = (0,0,0,255),width=2) 
		board =image.save("test.png") 
	def to_string(self): 
		string = "" 
		for y in range(15):
			for x in range(4): 
				temp = 0 
				mitsu = 3
				for i in range(4): 
					if x==3 and i>2: 
						True
					else: 
						if self.map[y][4*x+i]=='A': 
							temp += 3**mitsu 
						elif self.map[y][4*x+i]=='B': 
							temp += 2*3**mitsu 
						else : 
							True
					mitsu -=1
				#print(bit(ord(chr(temp))))
				string+=chr(temp) 
		return string 
def string_to_map(string): 
	gomoku_map = list()
	for y in range(15): 
		gomoku_map.append(list()) 
		for x in range(4): 
			char =ord(string[y * 4 + x])
			mitsu=3
			for i in range(4): 
				if x * 4 +i==15: 
					break 
				else: 
					gomoku_map[y].append(list()) 
					data =char//3**mitsu 
					if data == 1: 
						gomoku_map[y][x * 4 + i] = 'A' 
					elif data==2: 
						gomoku_map[y][x * 4 + i] = 'B' 
					else: 
						gomoku_map[y][x * 4 + i] = 'N'
					char=char%3**mitsu
				mitsu-=1
	return gomoku_map

def check_go(gomoku_map,x,y,cnt,direction,team):

	if gomoku_map[y][x] == team:
		if cnt == 4:
			return True
		if direction == 1:
			return check_go(gomoku_map,x+1,y,cnt+1,1,team)
		if direction == 2:
			return check_go(gomoku_map,x,y+1,cnt+1,2,team)
		if direction == 3:
			return check_go(gomoku_map,x+1,y+1,cnt+1,3,team)
		if direction == 4:
			return check_go(gomoku_map,x-1,y+1,cnt+1,4,team)
	else:
		return False
def check_win(gomoku_map):
	for y in range(0,15):
		for x in range(0,15):
			if gomoku_map[y][x] != 	'N':
				team_win = False
				if x<11:#R
					team_win = team_win or check_go(gomoku_map,x+1,y,1,1,gomoku_map[y][x])
				if y<11:#D
					team_win = team_win or check_go(gomoku_map,x,y+1,1,2,gomoku_map[y][x])
				if x<11 and y<11:#RD
					team_win = team_win or check_go(gomoku_map,x+1,y+1,1,3,gomoku_map[y][x])
				if x>3 and y<11:#LD
					team_win = team_win or check_go(gomoku_map,x-1,y+1,1,4,gomoku_map[y][x])

				if team_win == True:
					return gomoku_map[y][x]
	return 'N'



def new(bot,update):
	new_game = game()
	btn1 = [InlineKeyboardButton(text = "Left Up",callback_data="1A1"+new_game.to_string()),InlineKeyboardButton(text = "Up",callback_data="1A2"+new_game.to_string()),InlineKeyboardButton(text = "Right Up",callback_data="1A3"+new_game.to_string())]
	btn2 = [InlineKeyboardButton(text = "Left",callback_data="1A4"+new_game.to_string()),InlineKeyboardButton(text = "Middle",callback_data="1A5"+new_game.to_string()),InlineKeyboardButton(text = "Right",callback_data="1A6"+new_game.to_string())]
	btn3 = [InlineKeyboardButton(text = "Left Down",callback_data="1A7"+new_game.to_string()),InlineKeyboardButton(text = "Down",callback_data="1A8"+new_game.to_string()),InlineKeyboardButton(text = "Right Down",callback_data="1A9"+new_game.to_string())]
	button = InlineKeyboardMarkup([btn1,btn2,btn3])
	text = "Current player: O"
	new_game.draw()
	bot.sendPhoto(chat_id = update.message.chat.id,
							photo = open('test.png', 'rb'),
							caption = text,
							reply_markup = button)

def process_result(self,update,job_queue):
	#print(update)
	query = update.callback_query
	print(query.data[:3])
	if query.data[0] == '1':
		now_game = game()
		now_game.map = string_to_map(query.data[3:])
		now_game.tm_cnt = query.data[1]
		now_game.select = query.data[2]
		all_button = list()
		y_range = int((int(now_game.select)-1)/3)*5
		x_range = (int(now_game.select)-1)%3*5
		for j in range(y_range,y_range+5):
			button_x = list()
			for i in range(x_range,x_range+5):
				text = 'N'
				if now_game.map[j][i] == 'N':
					text=' '
				elif now_game.map[j][i] == 'A':
					text='O'
				elif now_game.map[j][i] == 'B':
					text ='X'
				print(len("2"+now_game.tm_cnt+chr(j)+chr(i)+now_game.to_string()))
				button_x.append(InlineKeyboardButton(text = text,callback_data="2"+now_game.tm_cnt+chr(j)+chr(i)+now_game.to_string()))
			all_button.append(button_x)
		all_button.append([InlineKeyboardButton(text = "Back",callback_data="B"+now_game.tm_cnt+now_game.to_string())])
		text = "Current player: "+query.from_user.first_name+" "+query.from_user.last_name
		if now_game.tm_cnt == 'A':
			text += "(O)\n"
		else:
			text += "(X)\n"
		if now_game.select == '1':
			text += "Left Up"
		elif now_game.select == '2':
			text += "Up"
		elif now_game.select == '3':
			text += "Right Up"
		elif now_game.select == '4':
			text += "Left"
		elif now_game.select == '5':
			text += "Middle"
		elif now_game.select == '6':
			text += "Right"
		elif now_game.select == '7':
			text += "Left Down"
		elif now_game.select == '8':
			text += "Down"
		elif now_game.select == '9':
			text += "Right down"

		bot.editMessageCaption(chat_id = query.message.chat.id,
							message_id = query.message.message_id,
							caption = text,
							reply_markup = InlineKeyboardMarkup(all_button))
	elif query.data[0] == '2':
		now_game = game()
		now_game.map = string_to_map(query.data[4:])
		now_game.tm_cnt = query.data[1]
		selectY = ord(query.data[2])
		selectX = ord(query.data[3])
		if now_game.map[selectY][selectX]!='N':
			bot.answer_callback_query(callback_query_id = query.id,text = "Unavailable position",show_alert=True)
			return
		else:
			now_game.map[selectY][selectX] = now_game.tm_cnt
			
			slct_cnt = 0
			for y in range(15):
				for x in range(15):
					if now_game.map[y][x] != "N":
						slct_cnt += 1

			if slct_cnt==1:
				text = "Start Game!"
			elif slct_cnt%2==1:
				text = "Player X's Choice"
			else:
				text = "Player O's choice"	

			if now_game.tm_cnt == 'A':
				now_game.tm_cnt = 'B'
			else:
				now_game.tm_cnt = 'A'

			final = check_win(now_game.map)
			if final!='N':
				text = query.from_user.first_name+" "+query.from_user.last_name + "Win!"
				bot.editMessageCaption(	chat_id = query.message.chat.id,
										message_id = query.message.message_id,
										caption = text,
										reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = "New Gomoku!",callback_data="N")]]))
			else:
				bot.deleteMessage(chat_id = query.message.chat.id,
							message_id = query.message.message_id)
				now_game.draw()
				btn1 = [InlineKeyboardButton(text = "Left Up",callback_data="1"+now_game.tm_cnt+"1"+now_game.to_string()),InlineKeyboardButton(text = "Up",callback_data="1"+now_game.tm_cnt+"2"+now_game.to_string()),InlineKeyboardButton(text = "Right Up",callback_data="1"+now_game.tm_cnt+"3"+now_game.to_string())]
				btn2 = [InlineKeyboardButton(text = "Left",callback_data="1"+now_game.tm_cnt+"4"+now_game.to_string()),InlineKeyboardButton(text = "Middle",callback_data="1"+now_game.tm_cnt+"5"+now_game.to_string()),InlineKeyboardButton(text = "Right",callback_data="1"+now_game.tm_cnt+"6"+now_game.to_string())]
				btn3 = [InlineKeyboardButton(text = "Left Down",callback_data="1"+now_game.tm_cnt+"7"+now_game.to_string()),InlineKeyboardButton(text = "Down",callback_data="1"+now_game.tm_cnt+"8"+now_game.to_string()),InlineKeyboardButton(text = "Right Down",callback_data="1"+now_game.tm_cnt+"9"+now_game.to_string())]
				button = InlineKeyboardMarkup([btn1,btn2,btn3])
				text = "Last player: "+query.from_user.first_name+" "+query.from_user.last_name
				if now_game.tm_cnt == 'A':
					text += "(X)\nCurrent Player:O"
				else:
					text += "(O)\nCurrent Player:X"
				print(len("1"+now_game.tm_cnt+"7"+now_game.to_string()))
				bot.sendPhoto(chat_id = query.message.chat.id,
										photo = open('test.png', 'rb'),
										caption = text,
										reply_markup = button)
	elif query.data[0] == 'B':
		now_game = game()
		now_game.map = string_to_map(query.data[2:])
		now_game.tm_cnt = query.data[1]
		btn1 = [InlineKeyboardButton(text = "Left Up",callback_data="1"+now_game.tm_cnt+"1"+now_game.to_string()),InlineKeyboardButton(text = "Up",callback_data="1"+now_game.tm_cnt+"2"+now_game.to_string()),InlineKeyboardButton(text = "Right Up",callback_data="1"+now_game.tm_cnt+"3"+now_game.to_string())]
		btn2 = [InlineKeyboardButton(text = "Left",callback_data="1"+now_game.tm_cnt+"4"+now_game.to_string()),InlineKeyboardButton(text = "Middle",callback_data="1"+now_game.tm_cnt+"5"+now_game.to_string()),InlineKeyboardButton(text = "Right",callback_data="1"+now_game.tm_cnt+"6"+now_game.to_string())]
		btn3 = [InlineKeyboardButton(text = "Left Down",callback_data="1"+now_game.tm_cnt+"7"+now_game.to_string()),InlineKeyboardButton(text = "Down",callback_data="1"+now_game.tm_cnt+"8"+now_game.to_string()),InlineKeyboardButton(text = "Right Down",callback_data="1"+now_game.tm_cnt+"9"+now_game.to_string())]
		button = InlineKeyboardMarkup([btn1,btn2,btn3])

		text = "Current player: "+query.from_user.first_name+" "+query.from_user.last_name
		if now_game.tm_cnt == 'A':
			text += "(O)\n"
		else:
			text += "(X)\n"

		bot.editMessageCaption(chat_id = query.message.chat.id,
							message_id = query.message.message_id,
							caption = text,
							reply_markup = button)
	elif query.data[0] == 'N':
		new_game = game()
		btn1 = [InlineKeyboardButton(text = "Left Up",callback_data="1A1"+new_game.to_string()),InlineKeyboardButton(text = "Up",callback_data="1A2"+new_game.to_string()),InlineKeyboardButton(text = "Right Up",callback_data="1A3"+new_game.to_string())]
		btn2 = [InlineKeyboardButton(text = "Left",callback_data="1A4"+new_game.to_string()),InlineKeyboardButton(text = "Middle",callback_data="1A5"+new_game.to_string()),InlineKeyboardButton(text = "Right",callback_data="1A6"+new_game.to_string())]
		btn3 = [InlineKeyboardButton(text = "Left Down",callback_data="1A7"+new_game.to_string()),InlineKeyboardButton(text = "Down",callback_data="1A8"+new_game.to_string()),InlineKeyboardButton(text = "Right Down",callback_data="1A9"+new_game.to_string())]
		button = InlineKeyboardMarkup([btn1,btn2,btn3])
		text = "Current player: O"
		new_game.draw()
		bot.sendPhoto(chat_id = query.message.chat.id,
						photo = open('test.png', 'rb'),
						caption = text,
						reply_markup = button)



@app.route('/hook', methods=['POST'])
def webhook_handler():
	"""Set route /hook with POST method will trigger this method."""
	if request.method == "POST":
		update = telegram.Update.de_json(request.get_json(force=True), bot)

		# Update dispatcher process that handler to process this message
		dispatcher.process_update(update)
	return 'ok'



# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(CommandHandler('new',new))
dispatcher.add_handler(CallbackQueryHandler(process_result, pass_job_queue=True))
if __name__ == "__main__":
	# Running server
	app.run(debug=True)