-

^smart typography$: mode.enable("user.smart_typography")
^plain typography$: mode.disable("user.smart_typography")

^unicode$: user.enable_unicode()
^no unicode$: user.disable_unicode()

insert <user.text>$: auto_insert(text)
erase: user.smart_delete_words(1)
