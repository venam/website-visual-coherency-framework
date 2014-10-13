create table internal_comparisons (
	id integer primary key,
	directory text,
	timestamp date
);

create table internal_comparisons_results (
	first_image text,
	second_image text,
	distance double,
	comparison_id integer
);

create table external_comparisons (
	id integer primary key,
	directory1 text,
	directory2 text,
	timestamp  date
);

create table external_comparisons_results (
	image text,
	distance double,
	comparison_id integer
);

.exit
.quit

