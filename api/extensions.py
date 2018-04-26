"""
This houses extensions shared across blueprints. They need to be abstracted from the api module so that we don't have
circular imports.
For  more information, check out
https://stackoverflow.com/questions/28784849/how-to-fix-circular-import-in-flask-project-using-blueprints-mysql-w-o-sqlalchem#28784938
"""
from flaskext.mysql import MySQL
mysql = MySQL()


#TODO: See if we should make this.
def executeSQLQuery(query) :
    conn = mysql.get_db()
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.commit()
    conn.commit()
    return cursor.fetchall()