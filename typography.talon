-

^unicode$:
	user.enable_unicode()

^no unicode$:
	user.disable_unicode()

insert <user.text>$: auto_insert(text)
erase: user.smart_delete_words(1)

smart typography: user.enable_smart_typography()
plain typography: user.disable_smart_typography()
