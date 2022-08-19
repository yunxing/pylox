# Add a rule `ast` to run `python gen_ast.py <current_dir>`
ast: gen_ast.py
	# python gen_ast.py <current_dir>
	python gen_ast.py $(abspath $(CURDIR))