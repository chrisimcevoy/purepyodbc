def test_execute(cursor):
    cursor.execute("select * from sys.tables;")
    row = cursor.fetchone()
    assert row
