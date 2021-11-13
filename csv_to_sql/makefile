PYTHON = python 

.PHONY: all clean

target_path = data/sql/
exec_path = parser/
targets_entities = faculties
targets_filepath = $(addsuffix .sql, $(addprefix $(target_path), $(targets_entities)))


all: parse 

parse: $(targets_filepath)

$(targets_filepath):
	@echo [ CREATING ] $(target_path)
	@mkdir $(target_path)
	@echo [ PARSING ] $@...
	@$(PYTHON) $(patsubst $(target_path)%.sql, $(exec_path)%.py, $@)


clean:
	@echo [ CLEANING ] ./data/sql/
	@rm -f -r $(target_path)

