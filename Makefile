
reset-db:
	@echo "Cleaning database..."
	docker exec bakery_postgres psql -U admin -d bakery_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	@echo "Restart your FastAPI server to have SQLAlchemy create the tables and then press Enter..."
	@read -p ""
	@echo "Populating with test data..."
	.venv/bin/python -m app.seed