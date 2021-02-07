import time
from talon import Context, Module, actions, settings, clip
import unicodedata

mod = Module()

mod.mode("smart_typography", "enable context-aware typography")

unicode = True

def clear_selection_clipboard():
	if clip.has_mode("select"):
		clip.set_text('', mode="select")

def raw_scan(num):
	if num < 0:
		first_action = actions.edit.extend_left
		second_action = actions.edit.extend_right
	else:
		first_action = actions.edit.extend_right
		second_action = actions.edit.extend_left

	for i in range(abs(num)):
		first_action()
	chars = actions.edit.selected_text()
	for i in range(len(chars)):
		second_action()

	return chars

def raw_delete_words(num):

	for i in range(num):

		# first just delete all spaces until next word
		clear_selection_clipboard()
		actions.edit.extend_word_left()
		before = actions.edit.selected_text()
		if before != '' and before[-1] in [" ", "\n"]:
			actions.edit.extend_word_right()
			actions.key("backspace")
			continue

		# if there were none, delete next word
		actions.key("backspace")

		# delete spaces before that as well
		clear_selection_clipboard()
		actions.edit.extend_left()
		before = actions.edit.selected_text()
		if before in [" ", "\n"]:
			actions.key("backspace")
		elif before != '':
			actions.edit.extend_right()


@mod.action_class
class Actions:
	def scan_chars_left(num: int = 1)->str:
		"""retrieve num characters to the left of the text cursor"""
		if clip.has_mode("select"):
			with clip.revert(mode="select"):
				clear_selection_clipboard()
				chars = raw_scan(-num)
		else:
			chars = raw_scan(-num)
		return chars

	def scan_chars_right(num: int = 1)->str:
		"""retrieve num characters to the right of the text cursor"""
		if clip.has_mode("select"):
			with clip.revert(mode="select"):
				clear_selection_clipboard()
				chars = raw_scan(num)
		else:
			chars = raw_scan(num)
		return chars

	def scan_chars_left_right(numl: int = 1, numr: int = 1) -> tuple[str, str]:
		"""retrieve num characters to the left and to the right of the text cursor"""
		if clip.has_mode("select"):
			with clip.revert(mode="select"):
				clear_selection_clipboard()
				charsl = raw_scan(-numl)
				clear_selection_clipboard()
				charsr = raw_scan(numr)
		else:
			charsl = raw_scan(-numl)
			charsr = raw_scan(numr)
		return charsl, charsr

	def smart_insert(
		txt: str,
		space_after: str = ".,!?:;)]}–“‘",
		no_space_before: str = ".,-!?:;)]}␣“‘’",
		ascii_replace: dict[str, str] = {
			'–':'-',
			'“':'"',  '”':'"',  '„':'"',
			"‘":"'",  "’":"'",  "‚":"'",
		},
		capitalize_after: str = ".!?"
	):
		"""context-aware insertion"""

		# delete whatever is currently selected
		actions.key(" ")
		actions.key("backspace")

		before, after = actions.user.scan_chars_left_right()

		squeeze_into_word = False
		if before != "" and unicodedata.category(before)[0] == 'L' \
		  and after != "" and unicodedata.category(after)[0] == 'L':
			squeeze_into_word = True

		if before != "" \
		  and (unicodedata.category(before)[0] == 'L' or before in space_after) \
		  and txt[0] not in no_space_before \
		  and not squeeze_into_word:
			actions.insert(' ')

		if before in capitalize_after or before == "":
			txt = txt[0].upper() + txt[1:]

		if not unicode:
			ascii = txt
			for c in ascii_replace:
				ascii = ascii.replace(c, ascii_replace[c])
			actions.insert(ascii)
		else:
			actions.insert(txt)

		if (
			after != ""
			and (
				txt[-1] in space_after
				or unicodedata.category(txt[-1])[0] == 'L'
			)
			and after not in ' \n\t'
			and after not in no_space_before
			and not squeeze_into_word
		):
			actions.insert(' ')

	def smart_delete_words(num: int):
		"""delete words and optionally spaces"""

		if clip.has_mode("select"):
			with clip.revert(mode="select"):
				clear_selection_clipboard()
				raw_delete_words(num)
		else:
			raw_delete_words(num)

	def count_words(txt: str) -> int:
		"""count number of words"""
		return len(str(txt).split())

	def enable_unicode():
		"""enable proper unicode punctuation"""
		global unicode
		unicode = True

	def disable_unicode():
		"""disable proper unicode punctuation"""
		global unicode
		unicode = False

ctx = Context()
ctx.matches = 'mode: user.smart_typography'

# overwrite talon's standard auto_insert
@ctx.action_class("main")
class main_action:
	def auto_insert(text: str):
		actions.user.smart_insert(text)
