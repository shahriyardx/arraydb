from unittest import TestCase, main

from arraydb import ArrayDb, Column


class TestDatabase(TestCase):
    """Tests the database"""

    def get_test_db(self):
        db = ArrayDb(
            columns=[
                Column("name"),
                Column("email"),
            ],
            data=[],
        )
        db.insert({"name": "Shahriyar", "email": "contact@shahriyar.dev"})

        return db

    def test_create_db(self):
        db = self.get_test_db()
        assert len(db.data) == 1

    def test_insert(self):
        db = self.get_test_db()
        db.insert({"name": "Anika"})

        assert db.find_first({"name": "Anika"}) is not None

    def test_find(self):
        db = self.get_test_db()
        f1 = db.find(where={"name": "Shahriyar"})
        f2 = db.find_first(where={"name": "Shahriyar"})

        assert isinstance(f1, list)
        assert f1[0]["name"] == "Shahriyar"
        assert f2["name"] == "Shahriyar"

    def test_upadte(self):
        db = self.get_test_db()

        old_data = db.find_first({"name": "Shahriyar"})
        db.update({"name": "Shahriyar"}, {"name": "Shahriyar Alam"})

        not_found = db.find_first({"name": "Shahriyar"})
        found = db.find_first({"name": "Shahriyar Alam"})

        assert old_data is not None
        assert not_found is None
        assert found is not None
        assert old_data["_id"] == found["_id"]

    def test_delete(self):
        db = self.get_test_db()
        db.delete({"name": "Shahriyar"})

        assert db.find_first({"name": "Shahriyar"}) is None

    def test_load(self):
        db = self.get_test_db()
        new_db = ArrayDb.load(db.serialize())

        assert sorted(db.column_names) == sorted(new_db.column_names)
        assert len(db.data) == len(new_db.data)


if __name__ == "__main__":
    main()
